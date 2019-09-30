#!/bin/env python
import os
import logging
from random import randint
import socket
import time
import boto3
from botocore import UNSIGNED
from botocore.config import Config

logger = logging.getLogger()
logger.setLevel(logging.INFO)
for lib in ["botocore", "boto3", "requests", "urllib3"]:
    logging.getLogger(lib).propagate = False


class OimSend:

    def __init__(self, env="ppd", send_s3="s3", location="ihp", custom_bucket=None, port=2878):
        self.send_s3 = send_s3
        self.port = port
        self.proxy = None
        self.location = location

        if self.location == "ihp":
            self.proxy = self._set_proxy()
        else:
            self.aws_account_id = self._get_aws_account_id()

        self.env = env

        self.wavefrontproxy = "wavefrontproxy-test.intuit.net"
        if self.env == "prd":
            self.wavefrontproxy = "wavefrontproxy.intuit.net"
        self.custom_bucket = custom_bucket
        self.s3_bucket = self._set_bucket()

    def _set_bucket(self):
        if self.custom_bucket:
            s3_bucket = self.custom_bucket
        elif self.location == 'ihp':
            s3_bucket = "intu-oim-prd-ihp-01-us-west-2" if self.env == "prd" else "intu-oim-dev-ihp-01-us-west-2"
        else:
            s3_bucket = 'intu-oim-%s-%s-us-west-2' % (self.env, self.aws_account_id[-1:])
        return s3_bucket

    def _set_proxy(self):
        proxy = None
        if self.location == "ihp":
            proxy = os.environ.get("https_proxy", "http://qy1prdproxy01.ie.intuit.net:80")
        return proxy

    def _post_to_s3(self, list_send):
        data = '\n'.join(list_send) + '\n'
        if self.location == 'ihp':
            client = boto3.client("s3", config=Config(signature_version=UNSIGNED, proxies={"https": self.proxy}))
        elif self.location == 'aws':
            client = boto3.client("s3")
        else:
            return "Invalid location parameter, please use aws or ihp"

        epoch_random = str(int(time.time())) + str(randint(1, 9000))
        send_wavefront = client.put_object(Body=data, Bucket=self.s3_bucket, Key=epoch_random,
                                           ACL="bucket-owner-full-control")
        if send_wavefront["ResponseMetadata"]["HTTPStatusCode"] == 200:
            logging.debug("sending:%s" % data)
            return "Metrics Sent: %s using s3 pipeline" % len(list_send)
        else:
            logging.error("failed to send to s3. Return code:%s" % (send_wavefront["ResponseMetadata"]["HTTPStatusCode"]))
            return "failed to send to s3: %s" % send_wavefront["ResponseMetadata"]["HTTPStatusCode"]

    def _connect_socket(self):
        sock = socket.socket()
        sock.settimeout(5)
        sock.connect((self.wavefrontproxy, self.port))
        return sock

    def _close_socket(self, sock):
        sock.close()

    def send_wave(self, list_send):
        if self.send_s3 != "s3":
            data = '\n'.join(list_send) + '\n'
            counter = 0
            while counter < 5:
                try:
                    sock = self._connect_socket()
                    sock.sendall(data.encode())
                    self._close_socket(sock)
                    return "Metrics Sent: %s using wavefrontproxy" % len(list_send)
                except Exception as exception:
                    logging.error("Could not connect to %s on port %d. ERROR:%s" % (self.wavefrontproxy, self.port,
                                                                                    exception))
                    counter += 1
                    time.sleep(3)
                    if counter == 4:
                        logging.error("data center proxy is down. Trying s3")
                        return self._post_to_s3(list_send)
        else:
            return self._post_to_s3(list_send)

    def _get_aws_account_id(self):
        client = boto3.client("sts")
        return client.get_caller_identity()["Account"]