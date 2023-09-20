# SPDX-License-Identifier: LGPL-2.1+

import urllib.parse
from typing import Generator

from mkosi.config import MkosiConfig
from mkosi.distributions import centos
from mkosi.installer.dnf import Repo


def join_mirror(config: MkosiConfig, link: str) -> str:
    assert config.mirror is not None
    return urllib.parse.urljoin(config.mirror, link)


class Installer(centos.Installer):
    @staticmethod
    def gpgurls() -> tuple[str, ...]:
        return (
            "https://access.redhat.com/security/data/fd431d51.txt",
        )

    @classmethod
    def _repository_variants(cls, config: MkosiConfig, repo: str) -> Generator[Repo, None, None]:
        if config.local_mirror:
            yield Repo(repo, f"baseurl={config.local_mirror}", cls.gpgurls())
        else:
            v = config.release
            yield Repo(
                f"ubi-{v}-{repo}-rpms",
                f"baseurl={join_mirror(config, f'ubi{v}/{v}/$basearch/{repo}/os')}",
                cls.gpgurls(),
            )
            yield Repo(
                f"ubi-{v}-{repo}-debug-rpms",
                f"baseurl={join_mirror(config, f'ubi{v}/{v}/$basearch/{repo}/debug')}",
                cls.gpgurls(),
                enabled=False,
            )
            yield Repo(
                f"ubi-{v}-{repo}-source",
                f"baseurl={join_mirror(config, f'ubi{v}/{v}/$basearch/{repo}/source')}",
                cls.gpgurls(),
                enabled=False,
            )
            if repo == "codeready-builder":
                yield Repo(
                    f"ubi-{v}-{repo}",
                    f"baseurl={join_mirror(config, f'ubi{v}/{v}/$basearch/{repo}/os')}",
                    cls.gpgurls(),
                    enabled=False,
                )

    @classmethod
    def repositories(cls, config: MkosiConfig, release: int) -> list[Repo]:
        return [
            *cls._repository_variants(config, "baseos"),
            *cls._repository_variants(config, "appstream"),
            *cls._repository_variants(config, "codeready-builder"),
        ]
