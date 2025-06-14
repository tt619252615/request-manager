{ buildPythonPackage, makeWrapper, pytestCheckHook, setuptools, wheel, loguru, click, numpy, pandas,requests,pymysql
, fastapi, uvicorn, pydantic, sqlalchemy, python-jose, mysqlclient, passlib, python-multipart, pydantic-settings, yapf, pylint, black, frontend }:

buildPythonPackage {
  pname = "request-manager";
  version = "0.1.0";

  src = ../../backend;
  
  format = "pyproject";

  nativeBuildInputs = [
    makeWrapper
    setuptools
    wheel
  ];

  propagatedBuildInputs = [
    fastapi
    uvicorn
    loguru
    pydantic
    sqlalchemy
    python-multipart
    requests
    pydantic-settings
    pymysql

    # Dev only packages
    yapf
    pylint
    black
  ];

  doCheck = false;

  postInstall = ''
    # Set up environment variables for the executable
    wrapProgram $out/bin/request-manager \
      --set BACKEND_FRONTEND ${frontend} \
      --set PYTHONPATH "$out/lib/python3.12/site-packages:$PYTHONPATH"
  '';
}