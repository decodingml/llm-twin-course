## What are Storage Buckets?

Storage buckets are fundamental entities used to store data in cloud storage services. They are essentially containers for data where you can upload, download, and manage files. Two of the most popular cloud storage services are Amazon S3 (Simple Storage Service) and Google Cloud Storage (GCS).

### Amazon S3

Amazon S3 buckets are used to store objects, which consist of data and its descriptive metadata. They are globally unique, and defined at the Universal Resource Locator (URL) level.

### Google Cloud Storage (GCS)

Google Cloud Storage buckets are similar to Amazon S3 buckets. They are used to store data objects in Google Cloud. Each bucket is associated with a specific project, and you can choose to make the bucket data public or private.

## Purpose in Our System

In our system, we use these storage buckets to store user code. When you write and save your code, it gets stored in either an S3 or GCS bucket. This allows us to securely store your code, retrieve it when needed, and even share it among multiple services or instances if required.

## How to Create Buckets

### Creating an Amazon S3 Bucket using AWS CLI

To create an Amazon S3 bucket, you can use the AWS CLI (Command Line Interface). Here's how:

1. First, install the AWS CLI on your machine. You can find the installation instructions [here](https://aws.amazon.com/cli/).
2. Configure the AWS CLI with your credentials:

```bash
aws configure
```

1. Create a new S3 bucket:

```bash
aws s3api create-bucket --bucket my-bucket-name --region us-west-2
```

Replace `my-bucket-name` with your desired bucket name and `us-west-2` with the AWS region you want to create your bucket in. For more information on S3 bucket creation, refer to the [AWS documentation](https://docs.aws.amazon.com/AmazonS3/latest/userguide/create-bucket-overview.html).

### Creating a Google Cloud Storage Bucket using `gsutil`

To create a Google Cloud Storage bucket, you can use the `gsutil` tool. Here's how:

1. First, install the Google Cloud SDK, which includes the `gsutil` tool. You can find the installation instructions [here](https://cloud.google.com/sdk/docs/install).
2. Authenticate your account:

```bash
gcloud auth login
```

1. Create a new GCS bucket:

```bash
gsutil mb -p project_id -c storage_class -l location gs://my-bucket-name
```

Replace `project_id` with the ID of your project, `storage_class` with the desired storage class for the bucket, `location` with the desired bucket location and `my-bucket-name` with your desired bucket name. For more information on GCS bucket creation, refer to the [Google Cloud Documentation](https://cloud.google.com/storage/docs/creating-buckets).

Remember, the bucket names must be unique across all existing bucket names in Amazon S3 or Google Cloud Storage.
