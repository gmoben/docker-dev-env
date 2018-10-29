import inspect
import tempfile
import re
import shutil

from collections import defaultdict, OrderedDict

import fire
import git
import six
import structlog

from pybin.common import configure_log

LOG = structlog.get_logger()
configure_log()


ALLOWED_FORMATS = ['dict', 'list', 'flat_list']
DEFAULT_FIELDS = ['hexsha', 'message']


class GitToolException(Exception):
    pass


def init_remote_repo(repo_dir, url, branch='master'):
    """Instantiate a local repo using a remote target and checkout a branch.

    :param string repo_dir: Directory where the local repo will be initialized
    :param string url: URL to the target remote repository
    :param string branch: remote branch to checkout
    :rtype: ``git.Repo``
    """
    log = LOG.bind(url=url, repo_dir=repo_dir, branch=branch)
    try:
        log.debug("Initializing local repo")
        repo = git.Repo.init(repo_dir)
        remote = repo.create_remote('origin', url)
        remote.fetch()
        remote.refs[branch].checkout()
        return repo
    except Exception as e:
        msg = 'Error fetching remote commits'
        log.exception(msg, exc_info=e)
        raise GitToolException(msg)


def format_fields(fields=[], include_defaults=False):
    if include_defaults:
        fields += DEFAULT_FIELDS

    field_set = set()
    if fields:
        if isinstance(fields, six.string_types):
            field_set.add(fields)
        elif isinstance(fields, (list, tuple, set)):
            [field_set.add(f) for f in fields]
        else:
            msg = "fields must be a string, list, or tuple"
            LOG.error(msg, fields=fields)
            raise GitToolException(msg)
    else:
        msg = "No fields supplied for extraction"
        LOG.error(msg, fields=fields)
        raise GitToolException(msg)

    return field_set


def validate_result_format(result_format):
    if result_format not in ALLOWED_FORMATS:
        msg = f'Invalid result format, must be one of {ALLOWED_FORMATS}'
        LOG.error(msg, result_format=result_format)
        raise GitToolException(msg)


def extract_commit_data(repo, fields, result_format, log=LOG):
    """Extract metadata from each commit in a ``git.Repo``.

    :param git.Repo repo: Repository instance
    :param iterable fields: Properties to extract from each commit. May be dot separated for nested objects.
    :param string result_format: Method to format entries extracted from each commit.
    :param BoundLogger log: Optionally supply a parent bound logger, otherwise default to the base logger.
    :return: List of extracted data objects formatted according to the ``result_format``
    """
    results = []
    commits = list(repo.iter_commits())
    if not commits:
        msg = "No commits found"
        log.error(msg, commits=commits)
        raise GitToolException(msg)

    log = log.bind(total_commits=len(commits))
    log.debug("Filtering commits", fields=fields)

    for c in commits:
        commit_metadata = dict() if result_format == 'dict' else []
        for f in fields:
            data = c
            try:
                for part in f.split('.'):
                    data = getattr(data, part)
                if isinstance(data, six.string_types):
                    data = data.strip()
            except AttributeError as e:
                msg = 'Commit missing an attribute'
                members = [x[0] for x in inspect.getmembers(data) if not x[0].startswith('_')]
                log.exception(msg, commit=c, attribute=f, data_obj=data, members=members, exc_info=e)
                raise GitToolException(msg)

            if result_format == 'dict':
                commit_metadata[f] = data
            else:
                commit_metadata.append(data)
        if result_format == 'flat_list':
            assert isinstance(commit_metadata, list)
            [results.append(x) for x in commit_metadata]
        else:
            results.append(commit_metadata)
    return results


class GitTool(object):
    """Utility class containing methods for manipulating and analyzing Git repositories"""

    @staticmethod
    def commits(url, *fields, include_defaults=True, result_format='list', preserve=False, repo_dir=None, limit=None):
        """Retrieve commit metadata from a remote git repository.

        :param string url: URL to the remote git repository.
        :param iterable fields: List of properties to return from each commit
        :param bool include_defaults: Set to False to skip inclusion of
        :returns: list of dicts containing the properties specified in `fields`
        """
        log = LOG.bind(url=url)

        validate_result_format(result_format)
        fields = format_fields(list(fields), include_defaults)

        if not repo_dir:
            repo_dir = tempfile.mkdtemp()
            log.info("Creating temporary folder for local repo", repo_dir=repo_dir)
        else:
            log.info("Using user supplied directory", repo_dir=repo_dir)

        log = log.bind(repo_dir=repo_dir)
        repo = init_remote_repo(repo_dir, url)

        try:
            results = extract_commit_data(repo, fields, result_format, log)
        except Exception as e:
            log.exception('Error processing commits', fields=fields)
            raise e
        finally:
            if not preserve:
                log.warning("Removing local repository (use --preserve to disable this behavior)")
                shutil.rmtree(repo_dir)
            else:
                log.debug("Leaving local repository in place")

        log.debug("Finished extracting commit metadata", results=results)

        if limit is not None:
            return results[:limit]
        return results

    @staticmethod
    def counts(url, key='author.email'):
        """Count the unique commits associated with a given commit attribute.

        :param string url: Remote URL or local path to a remote git repository.

        """
        LOG.info('Getting counts', url=url, key=key)
        authors = GitTool.commits(url, key, include_defaults=False, result_format='flat_list')
        counts = defaultdict(lambda: 0)
        for x in authors:
            if key == 'author.email':
                x = re.sub(r'@.+', '', x)
            counts[x] += 1

        return OrderedDict(reversed(sorted(counts.items(), key=lambda x: x[1])))


if __name__ == '__main__':
    fire.Fire(GitTool)
