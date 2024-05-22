### Introduction

This project aims to automate the process of creating CSV files for Correo Argentino and Fixy containing the orders for all Shopify stores. Additionally, it includes new store additions to enhance the functionality of the project.

### Workflow Diagram

To visualize the workflow of the project, refer to the following diagram: [Workflow Diagram](https://app.eraser.io/workspace/ZBk8qkWx9FUNUjj43sqO)

### Automated Order Processing Software

I developed a software that handles the daily task of retrieving unfulfilled orders from each business and generates labels for each order. This automation streamlines a process that was previously done manually. I successfully scaled this project to work with 12 local businesses currently.

For the development of this project, I utilized AWS cloud services. Specifically, I used Lambdas with cron jobs for daily execution due to their low costs and high scalability. I utilized SQS to send messages with all the stores to execute, ensuring that each store runs on a separate instance of each Lambda. CloudWatch logs were employed for logging purposes, while S3 buckets served as backups for each store. DynamoDB acted as a cache to prevent the repetition of labels that had already been processed. IAM roles were utilized for Lambda permissions, and MongoDB was used to securely store encrypted information for each store. Finally, the deployment was facilitated using Serverless.

### New Store Additions

1. **Company Field Addition**: A new field, "Company," has been added to the page.
2. **Checkout Placeholder Modification**:
   - Company label = Street
   - Address1 label = Number
   - Optional Address2 label = Floor and apartment (e.g., "2A")
3. **Checkout Configuration Page Modification**:
   3.1 Only email can be entered at the top of the page.
   3.2 A mandatory cell phone field has been added at the end of the checkout.
4. **API Integration**:
   - The API has been integrated into the store, and the token has been obtained. Read Orders permissions have been granted.
5. **AWS Secrets Integration**:
   - Credentials have been added to AWS Secrets.
6. **WhatsApp Group ID Retrieval**:
   - The ID of the WhatsApp group has been obtained.
7. **JSON File Creation**:
   - A JSON file has been created with the store name placed in AWS + _products.
8. **Deployment**:
   - Changes have been deployed to PROD and DEV using the following commands:
     - `sls deploy --stage prod`
     - `sls deploy --stage prod`
