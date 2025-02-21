import oci
import json
import argparse

# Lists existing instance configurations in the given compartment.
def list_instance_configurations(compartment_id, compute_mgmt_client):
    response = compute_mgmt_client.list_instance_configurations(compartment_id=compartment_id)
    instance_configs = response.data
    if not instance_configs:
        print("No instance configurations found.")
        return None
    print("\nAvailable Instance Configurations:")
    for idx, config in enumerate(instance_configs, 1):
        print(f"{idx}. {config.display_name} ({config.id})")
    choice = int(input("\nEnter the number of the instance config to use: ")) - 1
    return instance_configs[choice] if 0 <= choice < len(instance_configs) else None

# Fetches details of an instance configuration.
def get_instance_config_details(instance_config_id, compute_mgmt_client):
    response = compute_mgmt_client.get_instance_configuration(instance_config_id)
    return response.data

# Lists existing cluster networks in the given compartment.
def list_cluster_networks(compartment_id, compute_mgmt_client):
    response = compute_mgmt_client.list_cluster_networks(compartment_id=compartment_id)
    cluster_networks = response.data
    if not cluster_networks:
        print("No Cluster Networks found.")
        return None
    print("\nAvailable Cluster Networks:")
    for idx, cluster in enumerate(cluster_networks, 1):
        print(f"{idx}. {cluster.display_name} ({cluster.id})")
    choice = int(input("\nEnter the number of the Cluster Network to use: ")) - 1
    return cluster_networks[choice] if 0 <= choice < len(cluster_networks) else None

# Modifies the instance configuration JSON with the new SSH key.
def modify_instance_config(instance_config, new_ssh_key):
    instance_config_json = json.loads(str(instance_config))
    # Update SSH key
    if "metadata" in instance_config_json["instance_details"]["launch_details"]:
        instance_config_json["instance_details"]["launch_details"]["metadata"]["ssh_authorized_keys"] = new_ssh_key
    else:
        instance_config_json["instance_details"]["launch_details"]["metadata"] = {"ssh_authorized_keys": new_ssh_key}
    return instance_config_json

# Creates a new instance configuration with the updated SSH key.
def create_new_instance_config(compartment_id, instance_config_json, compute_mgmt_client):
    new_config_details = oci.core.models.CreateInstanceConfigurationDetails(
        compartment_id=compartment_id,
        display_name=instance_config_json["display_name"] + "-new",
        instance_details=oci.core.models.ComputeInstanceDetails(
            instance_type="compute",
            launch_details=oci.core.models.InstanceConfigurationLaunchInstanceDetails(
                availability_domain=instance_config_json["instance_details"]["launch_details"]["availability_domain"],
                compartment_id=instance_config_json["instance_details"]["launch_details"]["compartment_id"],
                metadata=instance_config_json["instance_details"]["launch_details"]["metadata"],
                shape=instance_config_json["instance_details"]["launch_details"]["shape"],
                source_details=oci.core.models.InstanceConfigurationInstanceSourceViaImageDetails(
                    source_type="image",
                    image_id=instance_config_json["instance_details"]["launch_details"]["source_details"]["image_id"]
                )
            )
        )
    )
    response = compute_mgmt_client.create_instance_configuration(new_config_details)
    return response.data

# Attaches the new instance configuration to the chosen cluster network.
def attach_instance_config_to_cluster_network(cluster_network_id, new_instance_config_id, compute_mgmt_client):
    # Step 1: Fetch the existing cluster network details
    try:
        cluster_network = compute_mgmt_client.get_cluster_network(cluster_network_id).data
    except oci.exceptions.ServiceError as e:
        print(f"Error fetching cluster network details: {e}")
        return
    # Step 2: Get existing instance pools inside this cluster network
    instance_pool_ids = [pool.id for pool in cluster_network.instance_pools]
    if not instance_pool_ids:
        print(f"No instance pools found in Cluster Network {cluster_network_id}. Cannot attach instance config.")
        return
    print(f"Found {len(instance_pool_ids)} instance pool(s) in Cluster Network.")
    # Step 3: Update each instance pool with the new instance configuration
    for pool_id in instance_pool_ids:
        update_pool_details = oci.core.models.UpdateInstancePoolDetails(
            instance_configuration_id=new_instance_config_id
        )
        try:
            response = compute_mgmt_client.update_instance_pool(
                instance_pool_id=pool_id,
                update_instance_pool_details=update_pool_details
            )
            print(f"\nSuccessfully updated Instance Pool {pool_id} with new Instance Config {new_instance_config_id}")
        except oci.exceptions.ServiceError as e:
            print(f"Failed to update Instance Pool {pool_id}: {e}")
    print("\nNow you can add new nodes to the cluster.")

def main():
    parser = argparse.ArgumentParser(description="Create and attach a new instance config with updated SSH key")
    parser.add_argument("--compartment-id", required=True, help="OCID of the compartment")
    args = parser.parse_args()

    compartment_id = args.compartment_id

    # Authenticate with OCI
    signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
    compute_mgmt_client = oci.core.ComputeManagementClient(config={}, signer=signer)

    # Step 1: List and Choose Instance Config
    chosen_instance_config = list_instance_configurations(compartment_id, compute_mgmt_client)
    if not chosen_instance_config:
        return

    # Step 2: Fetch Instance Config Details
    instance_config_details = get_instance_config_details(chosen_instance_config.id, compute_mgmt_client)

    # Step 3: Ask for SSH Key
    new_ssh_key = input("\nEnter new SSH Public Key: ")

    # Step 4: Modify Instance Config JSON with new SSH Key
    modified_config_json = modify_instance_config(instance_config_details, new_ssh_key)

    # Step 5: Create New Instance Config with Updated SSH Key
    new_instance_config = create_new_instance_config(compartment_id, modified_config_json, compute_mgmt_client)
    print(f"\nNew Instance Configuration Created: {new_instance_config.id}")

    # Step 6: List and Choose Cluster Network
    chosen_cluster_network = list_cluster_networks(compartment_id, compute_mgmt_client)
    if not chosen_cluster_network:
        return

    # Step 7: Attach New Instance Config to Chosen Cluster Network
    attach_instance_config_to_cluster_network(chosen_cluster_network.id, new_instance_config.id, compute_mgmt_client)
    print(f"\nInstance Configuration {new_instance_config.id} attached to Cluster Network {chosen_cluster_network.id}")

    # Final Message
    print("\nSuccess! Now you can add new nodes to the cluster using this instance configuration.")

if __name__ == "__main__":
    main()