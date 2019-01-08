#!/usr/bin/env python3
import os
import tarfile
import subprocess
import boto3
import shutil
import time
import json
import mimetypes
from time import sleep
from urllib.request import urlopen

TEMP_DIR = "/tmp/" #
CHUNK = 16 * 1024
EXTRA_DEBUG = True


def sendSNS(subject, message):
	client = boto3.client('sns')
	response = client.publish(
		TopicArn=SNS_TOPIC_ARN,
		Subject=subject,
		Message=message
	)

def download_extract(source, saveLocation, message):
	print(message)
	response = urlopen(source)
	with open(saveLocation, "wb") as f:
		while True:
			chunk = response.read(CHUNK)
			if not chunk:
				break
			f.write(chunk)
	tar = tarfile.open(saveLocation, "r:gz")
	topLevelDir = os.path.commonprefix(tar.getnames())
	if topLevelDir and os.path.isdir(TEMP_DIR + topLevelDir):
			print("%s exists, removing directory." % (TEMP_DIR + topLevelDir))
			shutil.rmtree(TEMP_DIR + topLevelDir)
			sleep(.1)
	tar.extractall(TEMP_DIR)
	# If the result is common folder, lets return that folder
	return TEMP_DIR + os.path.commonprefix(tar.getnames())

def s3_upload(source, target):
	# Upload files to S3, note, this doesn't handle deletes of old files that are no longer referenced
	counter = 0
	s3 = boto3.client('s3')
	for root, dirs, files in os.walk(source):
		for filename in files:
			# construct the full local path
			local_path = os.path.join(root, filename)
			# construct the full path
			relative_path = os.path.relpath(local_path, source)
			if EXTRA_DEBUG: print("Uploading %s..." % relative_path)
			
			s3.upload_file(local_path, target, relative_path, ExtraArgs={'StorageClass': 'REDUCED_REDUNDANCY', 'ContentType': mimetypes.guess_type(local_path)[0]})
			counter += 1
	print("Uploaded %s Files to %s" % (counter, target))

def cloudfront_invalidate(distributionId):
	cfront = boto3.client('cloudfront')
	response = cfront.create_invalidation(
		DistributionId=distributionId,
		InvalidationBatch={
			'Paths': {
				'Quantity': 1,
				'Items': [ '/*' ]
			},
			'CallerReference': str(time.time()) # Unique value to trigger invalidation
		}
	)

def theme_setup(siteDir, themeUrl, themeSaveLocation, finalThemeName):
	siteThemeDir = siteDir + "/themes/"
	if not os.path.isdir(siteThemeDir):
		os.mkdir(siteThemeDir)
	themeExtractLocation = download_extract(themeUrl, themeSaveLocation, "Downloading Theme")
	if os.path.isdir(siteThemeDir + finalThemeName):
		if EXTRA_DEBUG: print("%s exists, removing directory." % (siteThemeDir + finalThemeName))
		shutil.rmtree(siteThemeDir + finalThemeName)
		sleep(.25)
	os.rename(themeExtractLocation, siteThemeDir + finalThemeName)
	if EXTRA_DEBUG:
		sp = subprocess.run(["ls", siteThemeDir], capture_output=True)
		print("Theme Folders: " + sp.stdout.decode())

def my_handler(event, context):
	# -- Read in and set up variables --
	# This section is mandatory
	SITE_SOURCE_ARCHIVE = os.environ['SITE_SOURCE_ARCHIVE']
	HUGO_BINARY_ARCHIVE_URL = os.environ['HUGO_BINARY_ARCHIVE_URL']
	BUCKET_NAME = os.environ['BUCKET_NAME']
	
	
	# Theme, CloudFront and SNS are optional. However, both theme variables must be provided if one is.
	THEME_NAME =  os.environ.get('THEME_NAME') # The name the site expects
	THEME_ARCHIVE_URL = os.environ.get('THEME_ARCHIVE_URL')
	CLOUDFRONT_DISTRIBUTION_ID = os.environ.get('CLOUDFRONT_DISTRIBUTION_ID')
	SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')
	
	# You shouldn't need to change these:
	hugoTarball = TEMP_DIR + "hugo.tar.gz"
	siteTarball = TEMP_DIR + "site.tar.gz"
	themeTarball = TEMP_DIR + "theme.tar.gz"
	BUILD_TO_LOCATION = TEMP_DIR + "public"

	#print("Event: " + json.dumps(event))
	if ("action" not in event) or (event["action"] != "closed") or ("pull_request" not in event) or (event["pull_request"]["base"]["ref"] != "master"):
		if SNS_TOPIC_ARN:
			sendSNS("Publish Ignored","Message recieved but ignored as it doesn't match a closed master branch MR")
		return 204
	# This should be a closed merge to master
	
	download_extract(HUGO_BINARY_ARCHIVE_URL, hugoTarball, "Downloading Hugo")
	siteRootDir = download_extract(SITE_SOURCE_ARCHIVE, siteTarball, "Downloading Website")
	
	if THEME_NAME and THEME_ARCHIVE_URL:
		theme_setup(siteRootDir, THEME_ARCHIVE_URL, themeTarball, THEME_NAME)

	

	# Make the Hugo magic! You can add additional parameters to the array below.
	print("Building site with Hugo")
	hugoBuild = subprocess.run(["/tmp/hugo", "--cleanDestinationDir", "-s", siteRootDir, "-d", BUILD_TO_LOCATION], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
	if hugoBuild.returncode != 0:
		sendSNS("Build Fail", "Failed to build Hugo website for bucket " + BUCKET_NAME)
		raise Exception("Error Building Hugo, cannot continue.")
	if EXTRA_DEBUG:
		print("Resulting files in top-most directory:")
		subprocess.run(["ls","-l", BUILD_TO_LOCATION])

	s3_upload(BUILD_TO_LOCATION, BUCKET_NAME)
	cloudfront_invalidate(CLOUDFRONT_DISTRIBUTION_ID)
	if SNS_TOPIC_ARN:
		sendSNS("Website Publish Completed.","Automation has published the changes to " + BUCKET_NAME)
	return {'statusCode': 200,'body': "done"}

if __name__ == "__main__":
	my_handler('','')

