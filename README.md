# Cloud Foundry Container to Container Networking Demo

This demonstration code borrows heavily from the flask-echo-server
project.

This demonstrates the use of the Cloud Foundry container-to-container
networking code, how to configure it, and how to use it.  In this
example, the "frontend" serves both local data and when a specific
path is referenced ("/neighbor"), will use the C2C networking to
obtain additional information.

In particular, note that the backend is deployed in the
"apps.internal" domain (used for internal references), and is not
accessible from the outside.  The port number referenced is the port
used from VCAP variable, and directly accessed.  Note that this is
different from a usual application (which would be on port 80, by the
gorouter), since the gorouter is not used.

## Deploy frontend

```
$ cf push frontend -f manifest.yml --no-start
$ cf set-env frontend REMOTE_NEIGHBOR backend.apps.internal
$ cf set-env frontend REMOTE_PORT 8080
$ cf start frontend
```

## Deploy backend

```
$ cf push backend -f manifest.yml -d apps.internal
$ cf add-network-policy frontend --destination-app backend --port 8080 --protocol tcp
```

## Access front end (not using container networking)

Observe in the output that the neighbor is correctly identified, and
that the port is correct.

```
$ curl -s frontend.*<yourdomain>* | jq .
```

## Access front end, with backend reference

Observe the access via "cf logs frontend" -- these logs indicate the
remote IP address and port accessed.

```
$ curl -s frontend.*<yourdomain>*/neighbor | jq .
```
