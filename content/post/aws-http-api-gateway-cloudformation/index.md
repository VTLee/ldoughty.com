---
author: "Lee Doughty"
date: 2020-01-26
title: "AWS HTTP API Gateway CloudFormation Setup"
tags:
  - featured
  - aws
categories:
  - aws-articles
---

**Summary**: This article goes over AWS HTTP API Gateway (which is still in beta) for AWS Lambda targets. There's currently few examples, and a bug in a basic configuration that prevents the chain of services from working

<!--more-->

## HTTP API Gateway

HTTP API Gateway is AWS's new (as of this writing) feature to drop most features of REST API Gateway (meaning your code must handle most of these things) that nets you a 75% savings. For many users this isn't a huge deal, but this will be helpful to those that want to stick with API Gateway's benefits (Automatically multi-AZ, no AZ-to-AZ transfer costs with other AWS services), or otherwise don't want to invest in the effort to build your lambdas behind an ALB.

## CloudFormation Example

There's really no magic here, and what I really want to point out is simply that this CF is possible, though there is a bug with the implementation

```yaml
Transform: 'AWS::Serverless-2016-10-31'

Parameters: 
  CERTIFICATEARN:
      Type: String
  APIDOMAINNAME:
      Type: String
  
Resources:

  MyFunction:
    Type: 'AWS::Serverless::Function'
    Properties:
      FunctionName: MyFunction
      Handler: index.lambda_handler
      Runtime: python3.7
      InlineCode: |
                  import json
                  def lambda_handler(event, context):
                      return {
                          "statusCode": 200,
                          "headers": {
                              "Content-Type": "*/*"
                          }
                          "body": "Hello"
                      }
      MemorySize: 128
      Timeout: 29
      Tags:
        Name: MyFunction

  Gateway:
    Type: 'AWS::ApiGatewayV2::Api'
    DependsOn: MyFunction
    Properties:
      Name: Gateway-MyFunction
      Description: Lambda HTTP Gateway Proxy
      Target: !GetAtt [ MyFunction, Arn ]
      ProtocolType: "HTTP"

  DomainName:
    Type: 'AWS::ApiGatewayV2::DomainName'
    Properties:
      DomainName: !Ref APIDOMAINNAME
      DomainNameConfigurations:
        - EndpointType: REGIONAL
          CertificateArn: !Ref CERTIFICATEARN

  Logging:
    Type: AWS::Logs::LogGroup
    DependsOn: MyFunction
    Properties: 
      LogGroupName: !Join [/,["/aws/lambda", !Ref MyFunction ]]
      RetentionInDays: 5

  LambdaApiGatewayPermission:
    Type: AWS::Lambda::Permission
    Properties:
      Action: lambda:InvokeFunction
      FunctionName: !GetAtt [ MyFunction, Arn ]
      Principal: apigateway.amazonaws.com
      SourceArn: !Sub arn:aws:execute-api:${AWS::Region}:${AWS::AccountId}:${Gateway}/*
```

Quick note: Thanks to Colin Dellow @ https://cldellow.com for pointing out this missing `AWS::Lambda::Permission` above!

This is obviously a "Dummy" Script, it will stand up an API that returns Hello. You should plug in your own code by `CodeUri`. It _is_ worth nothing -- if you've never made an API Gateway before -- that the Timeout on your Lambda should be 30 seconds or less. This is a hard limit imposed by AWS, and can't be increased. You should also consider that, if an API is calling another API, a lower timeout might allow you the opportunity to retry if a call hangs/fails.

Anyway, once this CloudFormation is in place, you'll just need to provide an SSL Certificate Arn from Certificate Manager, and it's related domain. CloudFormation will spin up all the objects for you -- assuming you just want a basic, forward-everything default route. Adapt this to your needs!

## Slight bug

I did notice a minor problem with this CloudFormation template, and I'm not sure if it's due to a missing component on my side, or because this service is still in development. I needed to run the following command to give API Gateway permission to execute my lambda:

```sh
export ACCOUNT_NUMBER=123456789012
export REGION=us-east-1
export FUNCTION_NAME=MyFunction
export GATEWAYID=8r9luwzuag # Get the "ID" value from your API Gateway API Listing page
aws lambda add-permission \
  --statement-id AUniqueStatementId \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --function-name "arn:aws:lambda:${REGION}:${ACCOUNT_NUMBER}:function:${FUNCTION_NAME}" \
  --source-arn "arn:aws:execute-api:${REGION}:${ACCOUNT_NUMBER}:${GATEWAYID}/*"
```

This is a slight variation of the `Integrations` section _"Example policy statement"_ which allows all routes to call the Lambda, not just `$default`, which is seemingly necessary to function. Otherwise I constantly got either of these errors (depending on what configuration was currently in place as I explored this issue): _"{"message":"Internal Server Error"}"_ or _"{"message":"Not Found"}"_

I Hope this helps!
