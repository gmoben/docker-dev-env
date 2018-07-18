import logging
import os
import shlex
import subprocess

import structlog

LOG = structlog.get_logger()


def configure_log(log_level=None, **kwargs):
    """Setup structlog"""
    log_level = (os.environ.get('LOG_LEVEL', log_level) or 'INFO').upper()
    logging.basicConfig(level=log_level)

    kw = dict(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.dev.ConsoleRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    kw.update(**kwargs)

    structlog.configure_once(**kw)


def execute(cmd, shell=False, return_all=False, raise_on_exit=False):
    """Use Popen to execute a command string or array of arguments"""
    try:
        if isinstance(cmd, str) and not shell:
            cmd = shlex.split(cmd)

        process = subprocess.Popen(cmd,
                                   stderr=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   shell=shell)

        out, err = process.communicate()
        returncode = process.returncode

        if raise_on_exit:
            LOG.error("Nonzero exit code returned from external command",
                      out=out, err=err, code=returncode)
            raise Exception(f'Nonzero exit code ({returncode})')

        return (out, err, returncode)
    except Exception as e:
        LOG.exception("Error executing shell command", exc_info=e)
