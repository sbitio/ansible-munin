# *This role is abandoned.*

Munin
=====

Performs installation and configuration of Munin master, nodes and plugins.

Provides an action plugin to facilitate configuration of plugins. See below for
details.

This role is Work In Progress. See [`TODO` file](TODO.md) for some details.

For in-depth explanation of action plugins in roles please see
[sbitmedia.monit's README](https://github.com/sbitmedia/ansible-monit/blob/master/README.md).

Requirements
------------

Since Ansible doesn't support action plugins in roles, it is needed to
explicitly add the path to this role's action plugins in [`ansible.cfg`](https://github.com/ansible/ansible/blob/devel/examples/ansible.cfg).

Example:

```ini
action_plugins = ./contrib/roles/sbitmedia.munin/action_plugins
```

Happily, action_plugins supports relative paths. Paths are separated by colon
(`:`).


Role Variables
--------------

The role provides sane defaults, and respects configuration files provided by
the OS whenever possible.

Default variables are documented in [`defaults/main.yml`](defaults/main.yml).

Role variables are set per OS. See: [`vars/*.yml`](vars/).

See also the args accepted by `munin_plugin` in [`library/munin_plugin`](library/munin_plugin).


Example Usage
-------------

Using the role is straightforward, just include it and set overrides as needed.

Following playbook shows several examples of `munin_plugin` usage.

```yaml
- hosts: servers
  roles:
    - sbitmedia.munin

  tasks:
    - munin_plugin: 
      args:
        name: munin_update
      when: munin_role_master == true and munin_role_node == true

    - munin_plugin:
      args:
        name: if_
        instance: if_eth0

    - munin_plugin:
      args:
        name: postfix_mailvolume
        config: |
          group adm
          env.logfile mail.log
```

Leverage Munin in your roles
----------------------------

There's two ways to leverage this role in your own roles.

 * Hard dependency: add `sbitmedia.munin` as a dependency in your role and start
ruling your own checks with no drawbacks at all.

 * Soft dependency: use `sbitmedia.munin` when it is available. For this to
work, several thing need to happen:
1. the role must be included before yours.
1. calls to `munin_plugin` must be done this way, to avoid syntax errors in
Ansible:

```yaml
- name: Configure fail2ban service in Munin
  action: munin_plugin
  args:
    name: fail2ban
    config: |
      user root
      group root
  when: munin_node_service is defined
```

You can see a full-fledged pattern for integration of external services in
[sbitmedia.fail2ban](https://github.com/sbitmedia/ansible-fail2ban). See its
[`main.yml`](https://github.com/sbitmedia/ansible-fail2ban/blob/master/tasks/main.yml#L34)
along with [`external.yml`](https://github.com/sbitmedia/ansible-fail2ban/blob/master/tasks/external.yml)
and [`external/*`](https://github.com/sbitmedia/ansible-fail2ban/blob/master/tasks/external).


License
-------

BSD

Author Information
------------------

Jonathan Araña Cruz - SB IT Media, S.L.

