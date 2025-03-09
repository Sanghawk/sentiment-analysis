import boto3

class S3Manager:
    """
    A class for connecting to AWS S3 and performing common operations such as creating buckets,
    uploading files, downloading files, and listing objects. It also provides methods for
    compressing (gzip) and decompressing (ungzip) files.

    Attributes:
        s3_client (boto3.client): The boto3 S3 client.
        region_name (str): AWS region name.
    """

    def __init__(self, aws_access_key_id: str = None, aws_secret_access_key: str = None, region_name: str = 'us-east-1'):
        """
        Initializes the S3Client instance using boto3. If AWS credentials are not provided,
        boto3 will use the default credentials chain (environment variables, config files, IAM roles, etc.).

        Args:
            aws_access_key_id (str, optional): AWS access key ID.
            aws_secret_access_key (str, optional): AWS secret access key.
            region_name (str, optional): AWS region name. Defaults to 'us-east-1'.
        """
        self.region_name = region_name
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )
