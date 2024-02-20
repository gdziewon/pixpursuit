import { S3Client } from "@aws-sdk/client-s3";

let s3Client;

try {
  s3Client = new S3Client({
    endpoint: process.env.DO_SPACE_ENDPOINT,
    region: "ams3",
    credentials: {
      accessKeyId: process.env.DO_SPACE_ACCESS_KEY,
      secretAccessKey: process.env.DO_SPACE_SECRET_KEY,
    },
  });
} catch (error) {
  console.error('Failed to initialize S3 client:', error);
}

export default s3Client;
