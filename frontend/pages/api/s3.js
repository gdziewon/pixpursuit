import { S3Client } from "@aws-sdk/client-s3";

const s3Client = new S3Client({
  endpoint: process.env.NEXT_PUBLIC_DO_SPACE_ENDPOINT, // Ensure this is set in your .env file
  region: "ams3", // Replace with your Space region, e.g., "ams3"
  credentials: {
    accessKeyId: process.env.NEXT_PUBLIC_DO_SPACE_ACCESS_KEY, // Ensure these are set in your .env file
    secretAccessKey: process.env.NEXT_PUBLIC_DO_SPACE_SECRET_KEY,
  },
});

export default s3Client;
