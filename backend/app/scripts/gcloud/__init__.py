"""Google Cloud deployment helpers.

Google Cloud Run is **not a supported deployment target** at the moment; the
application is deployed with Docker on an EC2 instance instead.  Everything in
this package is kept so that a Cloud Run deployment can be revived later, and
nothing outside this package imports from it.

See ``backend/docs/source/developer-guide/google-cloud.md``.
"""
