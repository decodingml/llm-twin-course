## What are Virtual Machines?

Virtual Machines (VMs) are emulations of computer systems. They can run applications and services on a virtual platform, as if they were on a physical machine, while sharing the underlying hardware resources.

### VM size recommendations

The minimum VM size is `t3.small` in AWS or `e2-small` in GCP. Both configurations offer 2 vCPUs and 2GB of RAM. Note that if you are utilizing in-memory storage, the 2GB memory capacity can only accommodate a few tens of thousands of records. For larger datasets, opt for a machine with more RAM. The data loader functionality is CPU-intensive, so if you plan to use it, consider provisioning additional vCPUs.

The system comprises two components: poller and executor. The poller is a basic service, constrained in the Docker Compose file to use only 256MB of memory and 0.5 vCPU. The executor, which runs Superlinked along with a few minor additions, will consume the majority of the resources. It has no set limits in the Docker Compose file, so any resources not utilized by the poller will be allocated to the executor.

### Amazon EC2

Amazon Elastic Compute Cloud (EC2) is a part of Amazon's cloud-computing platform, Amazon Web Services (AWS). EC2 allows users to rent virtual computers on which to run their own computer applications.

### Google Cloud Compute Engine

Google Cloud Compute Engine delivers virtual machines running in Google's innovative data centers and worldwide fiber network. Compute Engine's tooling and workflow support enable scaling from single instances to global, load-balanced cloud computing.

## Creating an Amazon EC2 Instance using AWS CLI

To create an Amazon EC2 instance, you can use the AWS CLI. Here's how:

1. Install and configure the AWS CLI as described in the previous section.
2. Launch an EC2 instance:

```bash
aws ec2 run-instances --image-id ami-0abcdef1234567890 --count 1 --instance-type t3.small --key-name MyKeyPair --security-group-ids sg-903004f8 --subnet-id subnet-6e7f829e
```

Replace the `image-id`, `key-name`, `security-group-ids`, and `subnet-id` with your own values. The `image-id` is the ID of the AMI (Amazon Machine Image), `key-name` is the name of the key pair for the instance, `security-group-ids` is the ID of the security group, and `subnet-id` is the ID of the subnet.

For more information on creating key pairs, refer to the [AWS documentation](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html#having-ec2-create-your-key-pair). For a list of available regions, refer to the [AWS Regional Services List](https://aws.amazon.com/about-aws/global-infrastructure/regional-product-services/).

## Creating a Google Cloud Compute Engine VM using gcloud

To create a Google Cloud Compute Engine VM, you can use the `gcloud` command-line tool. Here's how:

1. Install and authenticate the Google Cloud SDK as described in the previous section.
2. Create a Compute Engine instance:

```bash
gcloud compute instances create my-vm --machine-type=e2-small --image-project=debian-cloud --image-family=debian-9 --boot-disk-size=50GB
```

Replace `my-vm` with your desired instance name. The `machine-type` is the machine type of the VM, `image-project` is the project ID of the image, `image-family` is the family of the image, and `boot-disk-size` is the size of the boot disk. Please use a `boot-disk-size` value over 20 GB.

Remember, you need to have the necessary permissions and quotas to create VM instances in both Amazon EC2 and Google Cloud Compute Engine.
