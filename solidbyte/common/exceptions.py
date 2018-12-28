# flake8: noqa
class SolidbyteException(Exception): pass
class DeploymentError(SolidbyteException): pass
class DeploymentValidationError(DeploymentError): pass
class CompileError(SolidbyteException): pass
class LinkError(CompileError): pass
