from infi.instruct import Struct, UBInt8, UBInt16, SumSizeArray, Field
from infi.instruct import FuncStructSelectorMarshal, StructFunc
from infi.instruct.errors import InstructError

from . import designators
from ... import PeripheralDeviceData
from .. import EVPDInquiryCommand

def _get_designator_header(stream, context):
    header = designators.DescriptorHeader.create_from_stream(stream, context)
    return header

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
    _context_ = dict(int_repr_format="0x%02x")

    def _determine_designator(self, stream, context=None):
        """according to spc4r30, page 613, table 531 - DESIGNATOR TYPE field"""

        header = _get_designator_header(stream, context)
        if header.designator_type in designators.SINGLE_TYPE_DESIGNATORS.keys():
            return designators.SINGLE_TYPE_DESIGNATORS[header.designator_type]
        if header.designator_type == 0x02:
            return _determine_eui_designator(header)
        if header.designator_type == 0x03:
            return _determine_naa_designator(stream, context)
        if header.designator_type >= 0x09 and header.designator_type <= 0x0F:
            # Reserved designator, we ignore it.
            return designators.Reserved_Designator
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
