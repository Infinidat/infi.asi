Overview
========

A cross-platform, asynchornous, SCSI interface in Python. In other words, you can use ASI to send SCSI commands.

Usage
-----

In this example, we will send a standard inquiry commands in a sync fashion.
We will use the context managers from infi.asi.executers to handle the device open/close:

```python
from infi.asi.executers import linux_sg as asi_context_linux
from infi.asi.executers import windows as asi_context_windows
```

Now we will use these context managers to send the CDB:

```python
>>> # Linux
>>> from infi.asi.cdb.inquiry.standard import StandardInquiryCommand
>>> from infi.asi.coroutines.sync_adapter import sync_wait
>>> with asi_context_linux("/dev/sg0") as asi:
...     command = StandardInquiryCommand()
...     response = sync_wait(command.execute(asi))
>>> print repr(response)
StandardInquiryData(peripheral_device=PeripheralDeviceData(type=5, qualifier=0), <7 bits padding>, rmb=1, version=5, response_data_format=2, hisup=1, normaca=1, <2 bits padding>, additional_length=31, protect=0, <2 bits padding>, 3pc=0, tpgs=0, acc=0, sccs=0, addr16=0, <3 bits padding>, multi_p=0, vs1=0, enc_serv=0, <1 bits padding>, vs2=0, cmd_que=0, <2 bits padding>, sync=0, wbus16=0, <2 bits padding>, t10_vendor_identification='NECVMWar', product_identification='VMware IDE CDR10', product_revision_level='1.00', extended=<none>)
```

On Windows, just use the other context manager.

Extending ASI for other CDBs is easy.
ASI translates SCSI check conditions and unit attentions to pretty exceptions. Here's an example:
```python
>>> from infi.asi.cdb.inquiry.vpd_pages.device_identification import DeviceIdentificationVPDPageCommand
>>> from infi.asi.errors import AsiCheckConditionError
>>> from infi.asi.coroutines.sync_adapter import sync_wait
>>> with asi_context_linux("/dev/sg2") as asi:
...     command = DeviceIdentificationVPDPageCommand()
...     try:
...         response = sync_wait(command.execute(asi))
...     except AsiCheckConditionError, error:
...         pass
>>> print repr(error)
AsiCheckConditionError("SCSI Check Condition status, sense SCSISenseDataFixed(response_code=SCSISenseResponseCode(code=112, valid=0), <1 bytes padding>, sense_key='ILLEGAL_REQUEST', <1 bits padding>, ili=0, eom=0, filemark=0, information=0, additional_sense_length=10, command_specific_information=0, additional_sense_code=AdditionalSenseCode(INVALID FIELD IN CDB: code=0x24, qualifier=0x00), field_replaceable_unit_code=0, sense_key_specific_high=64, sksv=1, sense_key_specific_low=0) [700005000000000a00000000240000c00001000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000]",)
```

Checking out the code
=====================

Run the following:

    easy_install -U infi.projector
    projector devenv build

Python 3
========

Support for Python 3 is experimental at this stage
