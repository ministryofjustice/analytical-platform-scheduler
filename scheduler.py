import os
import requests
import time
import json
import logging
from threading import Thread
from kubernetes import client, config
from flask import Flask, render_template
from flask_apscheduler import APScheduler

app = Flask(__name__) 

scheduler = APScheduler()
scheduler.api_enabled = True
scheduler.init_app(app)
scheduler.start()

config.load_incluster_config()
apps_v1_api = client.AppsV1Api()
networking_v1_api = client.NetworkingV1Api()

NAMESPACE = os.getenv('NAMESPACE')
DEPLOYMENT = os.getenv('DEPLOYMENT')
IDLE_URL = os.getenv('IDLE_URL')
MAX_IDLE_TIME = os.getenv('MAX_IDLE_TIME',600)
SCHEDULER_PORT = os.getenv('SCHEDULER_PORT')
SCHEDULER_SERVICE = os.getenv('SCHEDULER_SERVICE')
APP_SERVICE = os.getenv('APP_SERVICE')
APP_PORT = os.getenv('APP_PORT')
INGRESS = os.getenv('INGRESS')

logging.basicConfig(level=logging.DEBUG)

class Config(object):
    SCHEDULER_API_ENABLED = True

def set_replicas(apps_v1_api, DEPLOYMENT, NAMESPACE, count):
    deployment = apps_v1_api.patch_namespaced_deployment_scale(DEPLOYMENT, NAMESPACE, {'spec': {'replicas': count}})
    return deployment.spec

def check_replicas(apps_v1_api, DEPLOYMENT, NAMESPACE):
    readiness = apps_v1_api.read_namespaced_deployment(DEPLOYMENT,NAMESPACE)
    return readiness.status.ready_replicas

def set_ingress(networking_v1_api, INGRESS, NAMESPACE, IDLE_URL, SERVICE, PORT):
    body = dict({
    "spec": {
        "rules": [
            {
                "host": IDLE_URL, 
                "http": {
                    "paths": [
                        {
                            "pathType": "ImplementationSpecific",
                            "backend": {
                                "service": {
                                    "name": SERVICE, 
                                    "port": {
                                        "number": int(PORT)
                                    }
                                }
                            }
                        }
                    ]
                }
            }
        ]
    }
    })
    
    
    ingress = networking_v1_api.patch_namespaced_ingress(INGRESS, NAMESPACE, body)
    return ingress.spec


# scheduled job to periodically check to see if an instance has been used recently and sleep it if not
@scheduler.task('interval', id='check_activity', seconds=10)
def check_activity():
    
    last_active = requests.get("https://"+IDLE_URL+"/last-seen")

    if last_active.status_code != 200:
        logging.debug("Last seen endpoint not returning 200, bailing")
        return

    if  (int(time.time()-int(MAX_IDLE_TIME)) > int(last_active.text)):
        logging.info("Max idle time exceeded, sleeping deployment")
        # switch ingress over to scheduler
        ingress = set_ingress(networking_v1_api, INGRESS, NAMESPACE, IDLE_URL, SCHEDULER_SERVICE, SCHEDULER_PORT)

        # shut down app
        deployment = set_replicas(apps_v1_api,DEPLOYMENT,NAMESPACE,0)
    else:
        print("current time minus 600 is less than last activity")
    return

# endpoint to wake deployments if somebody tries to access them
@app.route('/') 
def catch_all(): # TODO: make this actually catch all
    global apps_v1_api
    global networking_v1_api

    readiness = check_replicas(apps_v1_api,DEPLOYMENT,NAMESPACE)
    logging.info("Replicas: %s" % readiness)
    set_replicas(apps_v1_api,DEPLOYMENT,NAMESPACE,1) 
    if readiness != None:
        set_ingress(networking_v1_api, INGRESS, NAMESPACE, IDLE_URL, APP_SERVICE, APP_PORT)
        logging.info("Replica query returning not null: switching ingress")
        return render_template("ready.html")

    return render_template("index.html")
