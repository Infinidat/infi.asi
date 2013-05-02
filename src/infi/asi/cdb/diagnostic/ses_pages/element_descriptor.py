from infi.instruct.buffer import Buffer, bytes_ref, be_int_field, list_field, buffer_field, after_ref, member_func_ref, bytearray_field
from . import PCVReceiveDiagnosticResultCommand, DiagnosticDataBuffer


class Descriptor(Buffer):
    descriptor_length = be_int_field(where=bytes_ref[2:4])
    descriptor = bytearray_field(where_when_pack=bytes_ref[4:], where_when_unpack=bytes_ref[4:descriptor_length + 4])


class ElementDescriptor(Buffer):
    def _possible_elements_num(self):
        return self.type_descriptor_header.possible_elements_num

    overall_element = buffer_field(where=bytes_ref[0:], type=Descriptor)
    individual_elements = list_field(where=bytes_ref[after_ref(overall_element):], type=Descriptor,
                                     n=member_func_ref(_possible_elements_num))

    def unpack(self, buffer, type_descriptor_header):
        self.type_descriptor_header = type_descriptor_header
        return super(ElementDescriptor, self).unpack(buffer)


# ses3r05: 6.1.10
class ElementDescriptorDiagnosticPagesData(DiagnosticDataBuffer):
    def _unpack_status_descriptor(self, buffer, index, **kwargs):
        descriptor = ElementDescriptor()
        bytes = descriptor.unpack(buffer, self.conf_page.type_descriptor_header_list[index])
        return descriptor, bytes

    def _possible_elements_num(self):
        return len(self.conf_page.type_descriptor_header_list)

    page_code = be_int_field(where=bytes_ref[0])
    page_length = be_int_field(where=bytes_ref[2:4])
    generation_code = be_int_field(where=bytes_ref[4:8])
    element_descriptors = list_field(where=bytes_ref[8:], type=ElementDescriptor,
                                     unpack_selector=_unpack_status_descriptor,
                                     n=member_func_ref(_possible_elements_num))


class ElementDescriptorDiagnosticPagesCommand(PCVReceiveDiagnosticResultCommand):
    def __init__(self, conf_page):
        super(ElementDescriptorDiagnosticPagesCommand, self).__init__(0x07, 65535, ElementDescriptorDiagnosticPagesData, conf_page)

__all__ = ["ElementDescriptorDiagnosticPagesCommand", "ElementDescriptorDiagnosticPagesData"]
