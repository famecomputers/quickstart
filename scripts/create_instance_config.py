#!/usr/bin/python

# This script created using Python OCI SDK to create new instance config from existing instance config where only image will be changed to new image.

import oci
import argparse

def list_instance_configurations(compartment_id):
    try:
        signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
        compute_management_client = oci.core.ComputeManagementClient(config={}, signer=signer)

        response = compute_management_client.list_instance_configurations(compartment_id=compartment_id)
        return response.data

    except oci.exceptions.ServiceError as e:
        print(f"An error occurred: {e}")
        return []

def list_custom_images(compartment_id):
    try:
        signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
        compute_client = oci.core.ComputeClient(config={}, signer=signer)

        response = oci.pagination.list_call_get_all_results(
            compute_client.list_images,
            compartment_id=compartment_id
        )

        if response.data:
            print(f"Custom Images in Compartment: {compartment_id}\n")
            custom_images = []
            for image in response.data:
                print(image.display_name)
                custom_images.append(image)
            return custom_images
        else:
            print(f"No custom images found in compartment {compartment_id}.")
            return []

    except oci.exceptions.ServiceError as e:
        print(f"Error retrieving custom images: {e}")
        return []

def get_instance_configuration(instance_configuration_id):
    try:
        signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
        compute_management_client = oci.core.ComputeManagementClient(config={}, signer=signer)

        response = compute_management_client.get_instance_configuration(instance_configuration_id)
        return response.data

    except oci.exceptions.ServiceError as e:
        print(f"An error occurred: {e}")
        return None

def create_instance_configuration(compartment_id, instance_configuration_details):
    try:
        signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
        compute_management_client = oci.core.ComputeManagementClient(config={}, signer=signer)

        # Construct the new instance configuration
        instance_config_details = oci.core.models.CreateInstanceConfigurationDetails(
            compartment_id=instance_configuration_details["compartment_id"],
            display_name=instance_configuration_details["display_name"],
            instance_details=oci.core.models.ComputeInstanceDetails(
                instance_type="compute",
                launch_details=oci.core.models.InstanceConfigurationLaunchInstanceDetails(
                    availability_domain=instance_configuration_details["instance_details"]["launch_details"]["availability_domain"],
                    compartment_id=instance_configuration_details["instance_details"]["launch_details"]["compartment_id"],
                    extended_metadata=instance_configuration_details["instance_details"]["launch_details"]["extended_metadata"],
                    ipxe_script=instance_configuration_details["instance_details"]["launch_details"]["ipxe_script"],
                    metadata=instance_configuration_details["instance_details"]["launch_details"]["metadata"],
                    shape=instance_configuration_details["instance_details"]["launch_details"]["shape"],
                    source_details=oci.core.models.InstanceConfigurationInstanceSourceViaImageDetails(
                        source_type="image",
                        image_id=instance_configuration_details["instance_details"]["launch_details"]["source_details"]["image_id"]
                    )
                )
            ),
            defined_tags=instance_configuration_details.get("defined_tags", {}),
            freeform_tags=instance_configuration_details.get("freeform_tags", {})
        )

        response = compute_management_client.create_instance_configuration(instance_config_details)
        return response.data

    except oci.exceptions.ServiceError as e:
        print(f"An error occurred: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Create a new instance configuration")
    parser.add_argument("--compartment-id", required=True, help="OCID of the compartment")
    args = parser.parse_args()

    compartment_id = args.compartment_id

    # List existing instance configurations
    instance_configurations = list_instance_configurations(compartment_id)
    if not instance_configurations:
        print("No instance configurations found.")
        return

    print("Existing Instance Configurations:")
    for i, ic in enumerate(instance_configurations):
        print(f"{i+1}. {ic.display_name} ({ic.id})")

    # Ask user to choose an instance configuration
    choice = int(input("Enter the number of the instance configuration to use: ")) - 1
    chosen_instance_configuration_id = instance_configurations[choice].id

    # List custom images
    custom_images = list_custom_images(compartment_id)
    if not custom_images:
        print("No custom images found.")
        return

    print("\nCustom Images:")
    for i, img in enumerate(custom_images):
        print(f"{i+1}. {img.display_name} ({img.id})")

    # Ask user to choose a custom image
    choice = int(input("Enter the number of the custom image to use: ")) - 1
    chosen_custom_image_id = custom_images[choice].id

    # Get the chosen instance configuration
    existing_instance_configuration = get_instance_configuration(chosen_instance_configuration_id)
    if not existing_instance_configuration:
        print("Failed to fetch instance configuration details.")
        return

    # Create a new instance configuration with the chosen custom image
    new_instance_configuration_details = {
        "compartment_id": existing_instance_configuration.compartment_id,
        "display_name": existing_instance_configuration.display_name + "-new",
        "instance_details": {
            "instance_type": existing_instance_configuration.instance_details.instance_type,
            "launch_details": {
                "availability_domain": existing_instance_configuration.instance_details.launch_details.availability_domain,
                "compartment_id": existing_instance_configuration.instance_details.launch_details.compartment_id,
                "create_vnic_details": existing_instance_configuration.instance_details.launch_details.create_vnic_details,
                "extended_metadata": existing_instance_configuration.instance_details.launch_details.extended_metadata,
                "ipxe_script": existing_instance_configuration.instance_details.launch_details.ipxe_script,
                "metadata": existing_instance_configuration.instance_details.launch_details.metadata,
                "shape": existing_instance_configuration.instance_details.launch_details.shape,
                "source_details": {
                    "image_id": chosen_custom_image_id
                }
            }
        },
        "defined_tags": existing_instance_configuration.defined_tags,
        "freeform_tags": existing_instance_configuration.freeform_tags
    }

    # Create the new instance configuration
    new_instance_configuration = create_instance_configuration(compartment_id, new_instance_configuration_details)
    if new_instance_configuration:
        print(f"\nCreated new instance configuration with ID {new_instance_configuration.id}")
    else:
        print("\nFailed to create new instance configuration.")

if __name__ == "__main__":
    main()
