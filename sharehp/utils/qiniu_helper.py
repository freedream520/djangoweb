import qiniu.rs
import qiniu.conf
import qiniu.io
import config
from ..exception import ConfigArgumentError
from ..exception import QiniuUploadFileError

_ACCESS_KEY = config.get_config("QINIU_ACCESS_KEY")
_SECRET_KEY = config.get_config("QINIU_SECRET_KEY")
_STATIC_NAME = config.get_config("QINIU_STATIC_NAME")

if not _ACCESS_KEY or not _SECRET_KEY or not _STATIC_NAME:
    raise ConfigArgumentError("qiniu config is invalid!")

qiniu.conf.ACCESS_KEY = _ACCESS_KEY
qiniu.conf.SECRET_KEY = _SECRET_KEY

policy = qiniu.rs.PutPolicy(_STATIC_NAME)
uptoken = policy.token()


def upload(filepath, key):
    try:
        ret, err = qiniu.io.put_file(uptoken, key, filepath)
    except Exception, err: # catch all exception TODO log
        raise QiniuUploadFileError(err)
    else:
        if err is not None:
            raise QiniuUploadFileError(err)


