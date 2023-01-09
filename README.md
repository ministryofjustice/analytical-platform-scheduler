# Analytical Platform Tools Scheduler

The Analytical Platform Tools Scheduler is used to idle Kubernetes pods when they the main container in that pod is not in use.

Using the presence of a last-activity endpoint in the relevant [RStudio](https://github.com/ministryofjustice/analytical-platform-nginx-proxy),
or [Jupyterlab](https://github.com/ministryofjustice/analytical-platform-nginx-jupyter) auth proxy,
this application will idle the main service until it receives traffic at which point it will reconstitute the service.


## Installing the scheduler

To install Analytical Platform Tools Scheduler, follow these steps, ideally within a virtual environment:

```
python -m pip install -r requirements.txt
```

## Configuring the scheduler

| Variable | Default | Description  |
|---|---|---|
| NAMESPACE | None | The namespace containing the service |
| DEPLOYMENT | None | The deployment to be idled, eg rstudio-user-rstudio |
| IDLE_URL | None |   |
| MAX_IDLE_TIME | 600| The length of time to wait for the service to be idle before shutting it down |
| SCHEDULER_PORT | None | Port scheduler runs on, set to 5000  |
| SCHEDULER_SERVICE | None | Name of the service that is created as a target for the ingress (see helm chart) |
| APP_SERVICE | None | Name of the kubernetes service that the ingress uses for the app (app = rstudio/jupyter)  |
| APP_PORT | None | Port that the app listens on |
| INGRESS | None | Name of the ingress that will flip between the app and the scheduler |

## Running the scheduler

To use the scheduler you can run it with:

```
python scheduler.py
```

