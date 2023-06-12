# usage compartment_id

import os
import sys

import oci

from oci import config
from oci import core
from oci import functions
from oci import identity
from oci import pagination

from oci.core import models as core_models
from oci.functions import models as fn_models

config = oci.config.from_file()
ComputeClient = oci.core.ComputeClient(config)
compute_client = oci.core.ComputeClient(config)
identity_client = oci.identity.IdentityClient(config)
virtual_network_client = oci.core.VirtualNetworkClient(config)
compartment_id = sys.argv[1]
response = oci.pagination.list_call_get_all_results(ComputeClient.list_instances, compartment_id=compartment_id)



print(response.data)
list_vnic_attachments_response = oci.pagination.list_call_get_all_results(
        compute_client.list_vnic_attachments,
        compartment_id  #, instance_id=instance.id
    )
vnic_attachments = list_vnic_attachments_response.data
print("vnic_attachments")
print(vnic_attachments)

vnic_attachment = vnic_attachments[0]
get_vnic_response = virtual_network_client.get_vnic(vnic_attachment.vnic_id)
vnic = get_vnic_response.data

print('Virtual Network Interface Card')
print('==============================')
print('{}'.format(vnic))
print()

#vnic_id = compute_client.list_vnic_attachments(
#        cd_compartment_id, instance_id=instanceId).data[0].vnic_id
private_ip = virtual_network_client.get_vnic(vnic_attachment.vnic_id).data.private_ip
print("private ip")
print(private_ip)

public_ip = virtual_network_client.get_vnic(vnic_attachment.vnic_id).data.public_ip
print("public_ip")
print(public_ip)

def get_availability_domain(identity_client, compartment_id):
    print("get_availability_domain compartment_id "+ compartment_id)
    list_availability_domains_response = oci.pagination.list_call_get_all_results(
        identity_client.list_availability_domains,
        compartment_id
    )
    # For demonstration, we just return the first availability domain but for Production code you should
    # have a better way of determining what is needed

    domains = list_availability_domains_response.data
    if len(domains) == 0:
        raise RuntimeError('No available domain was found.')
    print(domains)
    vm_domains = list(filter(lambda domain: domain.name.endswith("AD-3"), domains))
    #vm_shapes = list(filter(lambda shape: shape.shape.startswith("VM"), shapes))
    availability_domain = vm_domains[0]

    print()
    print('Running in Availability Domain: {}'.format(availability_domain.name))

    return availability_domain
def get_shape(compute_client, compartment_id, availability_domain):
    list_shapes_response = oci.pagination.list_call_get_all_results(
        compute_client.list_shapes,
        compartment_id,
        availability_domain=availability_domain.name
    )
    shapes = list_shapes_response.data
    if len(shapes) == 0:
        raise RuntimeError('No available shape was found.')

    vm_shapes = list(filter(lambda shape: shape.shape.startswith("VM.Standard.E2.1.Micro"), shapes))
    if len(vm_shapes) == 0:
        raise RuntimeError('No available VM shape was found.')

    # For demonstration, we just return the first shape but for Production code you should have a better
    # way of determining what is needed
    shape = vm_shapes[0]

    print('Found Shape: {}'.format(shape.shape))

    return shape

ad = get_availability_domain(identity_client,compartment_id)
OPERATING_SYSTEM = 'Oracle Linux'
list_images_response = oci.pagination.list_call_get_all_results(
    compute_client.list_images,
    compartment_id,
    operating_system=OPERATING_SYSTEM,
    shape=get_shape(compute_client,compartment_id,ad).shape
)
'''
images = list_images_response.data
vm_images = list(filter(lambda image: image.operating_system_version.startswith("8"), images))
print("vm_images")
print(vm_images)
if len(vm_images) == 0:
    raise RuntimeError('No available image was found.')

# For demonstration, we just return the first image but for Production code you should have a better
# way of determining what is needed
image = images[0]

print('Found Image: {}'.format(image.id))
print()
'''
