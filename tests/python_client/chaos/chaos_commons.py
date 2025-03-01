import os
import threading
import glob
import delayed_assert
from chaos import constants
from yaml import full_load
from utils.util_log import test_log as log


def check_config(chaos_config):
    if not chaos_config.get('kind', None):
        raise Exception("kind is must be specified")
    if not chaos_config.get('spec', None):
        raise Exception("spec is must be specified")
    if "action" not in chaos_config.get('spec', None):
        raise Exception("action is must be specified in spec")
    if "selector" not in chaos_config.get('spec', None):
        raise Exception("selector is must be specified in spec")
    return True


def reset_counting(checkers={}):
    for ch in checkers.values():
        ch.reset()


def gen_experiment_config(yaml):
    with open(yaml) as f:
        _config = full_load(f)
        f.close()
    return _config


def start_monitor_threads(checkers={}):
    threads = {}
    for k, ch in checkers.items():
        t = threading.Thread(target=ch.keep_running, args=())
        t.start()
        threads[k] = t
    return threads


def get_env_variable_by_name(name):
    """ get env variable by name"""
    try:
        env_var = os.environ[name]
        log.debug(f"env_variable: {env_var}")
        return str(env_var)
    except Exception as e:
        log.debug(f"fail to get env variables, error: {str(e)}")
        return None


def get_chaos_yamls():
    chaos_env = get_env_variable_by_name(constants.CHAOS_CONFIG_ENV)
    if chaos_env is not None:
        if os.path.isdir(chaos_env):
            log.debug(f"chaos_env is a dir: {chaos_env}")
            return glob.glob(chaos_env + 'chaos_*.yaml')
        elif os.path.isfile(chaos_env):
            log.debug(f"chaos_env is a file: {chaos_env}")
            return [chaos_env]
        else:
            # not a valid directory, return default
            pass
    log.debug("not a valid directory or file, return default")
    return glob.glob(constants.TESTS_CONFIG_LOCATION + constants.ALL_CHAOS_YAMLS)


def reconnect(conn, host, port):
    conn.add_connection(default={"host": host, "port": port})
    return conn.connect(alias='default')
