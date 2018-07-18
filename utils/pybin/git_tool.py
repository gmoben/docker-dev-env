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


class GitToolException(Exception):
    pass


class GitTool(object):

    @staticmethod
    def commits(url, *fields, extra_fields=None, dicts=False, keep_dir=False, path=None, flatten=False):
        """Retrieve commit metadata from a remote git repository.

        :param string url: URL to the remote git repository.
        :param iterable fields: List of properties to return from each commit
        :returns: list of dicts containing the properties specified in `fields`
        """

        log = LOG.bind(url=url)
        if len(fields) == 0:
            fields = ['hexsha', 'message']

        if extra_fields:
            # Make sure it's a list so we can append to it
            fields = list(fields)
            if isinstance(extra_fields, six.string_types):
                fields.append(extra_fields)
            elif isinstance(extra_fields, (list, tuple)):
                [fields.append(f) for f in extra_fields]
            else:
                msg = "extra_fields must be a string, list, or tuple"
                log.error(msg, fields=fields, extra_fields=extra_fields)
                raise GitToolException(msg)

        if not path:
            tempdir = tempfile.mkdtemp()
            log.info("Creating temporary git repo from url", url=url, path=tempdir)
        else:
            log.info("Using user supplied directory", url=url, path=path)

        try:
            repo = git.Repo.init(tempdir)
            remote = repo.create_remote('origin', url)
            remote.fetch()
            remote.refs['master'].checkout()
        except Exception as e:
            log.exception('Error fetching remote commits, removing temp dir', path=tempdir)
            shutil.rmtree(tempdir)
            raise

        try:
            metadata = []
            commits = list(repo.iter_commits())
            if not commits:
                msg = "No commits found"
                log.error(msg, commits=commits)
                raise GitToolException(msg)

            log = log.bind(total_commits=len(commits))
            log.info("Filtering commits", fields=fields)

            for c in commits:
                commit_metadata = {} if dicts else []
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
                        return
                    if dicts:
                        commit_metadata[f] = data
                    else:
                        commit_metadata.append(data)
                if not dicts and flatten:
                    [metadata.append(x) for x in commit_metadata]
                else:
                    metadata.append(commit_metadata)
            return metadata
        except Exception as e:
            log.exception('Error processing commits', fields=fields)
            raise e
        finally:
            if not keep_dir:
                LOG.info("Removing temporary directory", path=tempdir)
                shutil.rmtree(tempdir)
            else:
                LOG.info("Leaving temporary directory in place", path=tempdir)

    @staticmethod
    def counts(url, key='author.email'):
        authors = GitTool.commits(url, key, flatten=True)
        counts = defaultdict(lambda: 0)
        for x in authors:
            if x.startswith('you@example.com'):
                continue
            # x = re.sub(r'pindropsecurity', 'pindrop', x)
            x = re.sub(r'@.+', '', x)
            counts[x] += 1

        return OrderedDict(reversed(sorted(counts.items(), key=lambda x: x[1])))


if __name__ == '__main__':
    fire.Fire(GitTool)
