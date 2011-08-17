
from infi.instruct import Struct, FixedSizeString, UBInt8, UBInt16, SumSizeArray, Field
from infi.instruct import FuncStructSelectorMarshal, StructFunc
from infi.instruct.errors import InstructError

from . import designators
from ... import PeripheralDeviceData
from .. import EVPDInquiryCommand
from infi.asi.cdb.inquiry.vpd_pages.device_identification.designators import SCSINameDesignator

def _get_designator_header(stream, context):
    header = designators.DescriptorHeader.create_from_stream(stream, context)
    return header

def _get_designators_by_type_dict(header):
    """Some designators cannot be generally described because of their weird structure.
    This method creates a copy of the SINGLE_TYPE_DESIGNATORS dictionary and updates it with those
    designators that are built specifically by the header"""
    class T10VendorIDDesignator(designators.T10VendorIDDesignator):
        _fields_ = designators.DescriptorHeaderFields + [FixedSizeString("t10_vendor_identification", 8),
                                             FixedSizeString("vendor_specific_identifier",
                                                             header.designator_length - 8)]
    # BUG: INSTRUCT-7
    class SCSINameDesignator(designators.SCSINameDesignator):
        _fields_ = designators.DescriptorHeaderFields + \
                    [FixedSizeString("scsi_name_string", header.designator_length)]

    # BUG: INSTRUCT-7
    class VendorSpecificDesignator(designators.VendorSpecificDesignator):
        _fields_ = designators.DescriptorHeaderFields + \
                    [FixedSizeString("vendor_specific_identifier", header.designator_length)]

    # For the designators created above that needs to be custom built
    DESIGNATORS_BY_TYPE = designators.SINGLE_TYPE_DESIGNATORS.copy()
    DESIGNATORS_BY_TYPE.update({
                                0x00: VendorSpecificDesignator,
                                0x01: T10VendorIDDesignator,
                                0x08: SCSINameDesignator
                                })
    return DESIGNATORS_BY_TYPE

def _determine_eui_designator(header):
    key = header.designator_length
    if key in designators.EUI64_BY_LENGTH.keys():
        return designators.EUI64_BY_LENGTH[key]
    raise InstructError("unknown reserved designator length: %d" % key)

def _determine_naa_designator(stream, context):
    naa_header = designators.NAA_Header.create_from_stream(stream, context)
    key = naa_header.naa
    if key in designators.NAA_BY_TYPE.keys():
        return designators.NAA_BY_TYPE[key]
    InstructError("unknown reserved naa field: %d" % key)

# spc4r30: 7.8.15 (page 641)
class DeviceIdentificationVPDPageData(Struct):

    def _determine_designator(self, stream, context=None):
        """according to spc4r30, page 613, table 531 - DESIGNATOR TYPE field"""

        header = _get_designator_header(stream, context)
        DESIGNATORS_BY_TYPE = _get_designators_by_type_dict(header)

        if header.designator_type in DESIGNATORS_BY_TYPE.keys():
            return DESIGNATORS_BY_TYPE[header.designator_type]
        if header.designator_type == 0x02:
            return _determine_eui_designator(header)
        if header.designator_type == 0x03:
            return _determine_naa_designator(stream, context)
        raise InstructError("unknown designator type: %d" % header.designator_type)

    _fields_ = [
                Field("peripheral_device", PeripheralDeviceData),
                UBInt8("page_code"),
                SumSizeArray("designators_list", UBInt16,
                             FuncStructSelectorMarshal(StructFunc(_determine_designator), (0, 252))),
                ]

# spc4r30: 7.8.5
class DeviceIdentificationVPDPageCommand(EVPDInquiryCommand):
    def __init__(self):
        super(DeviceIdentificationVPDPageCommand, self).__init__(0x83, 255, DeviceIdentificationVPDPageData)

__all__ = ["DeviceIdentificationVPDPageCommand", "DeviceIdentificationVPDPageData"]
