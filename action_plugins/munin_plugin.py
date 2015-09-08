import os
from ansible import utils
from ansible.utils.template import template
from ansible.runner.return_data import ReturnData
from ansible.callbacks import callback_plugins

class ActionModule(object):

    def __init__(self, runner):
        self.runner = runner

    def run(self, conn, tmp, module_name, module_args, inject, complex_args=None, **kwargs):
        if inject['munin_role_node'] is False:
            raise Exception("munin_plugin: Target host is not a munin node!")

        # Load up options.
        options  = {}
        if complex_args:
            options.update(complex_args)

        options.update(utils.parse_kv(module_args))

        name = options.get('name')
        instance = options.get('instance', name)
        plugin_file = options.get('file', None)
        config = options.get('config', None)
        changed = False

        # Copy plugin file.
        if plugin_file is not None:
            module_args = 'src=%s dest=%s' % (plugin_file, dest)
            return_data = self.runner._execute_module(conn, tmp, 'copy', module_args, inject=inject)
            #TODO# Check result.
            if return_data.result.has_key('failed'):
                return return_data
            elif return_data.result['changed']:
                changed = True

        # Ensure plugin path.
        if plugin_file is not None:
            plugin_path = os.path.join(inject['munin_node_dir_plugins_custom'], name)
        else:
            plugin_path = os.path.join(inject['munin_node_dir_plugins_share'], name)

        # Create symlink to plugin.
        path = os.path.join(inject['munin_node_dir_plugins'], instance)
        module_args = 'state=link path=%s src=%s' % (path, plugin_path)
        return_data = self.runner._execute_module(conn, tmp, 'file', module_args, inject=inject)
        if return_data.result.has_key('failed'):
            return return_data
        elif return_data.result['changed']:
            changed = True

        # Set plugin configuration.
        if config is not None:
            action_path = utils.plugins.action_loader.find_plugin(module_name)
            src = os.path.realpath(os.path.dirname(action_path) + '/../templates/plugin_conf.j2')
            dest = os.path.join(inject['munin_node_dir_plugins_conf'], '%s.conf' % (instance))

            inject['instance'] = instance
            inject['config'] = config
            module_args = 'mode=600 src=%s dest=%s' % (src, dest)
            handler = utils.plugins.action_loader.get('template', self.runner)
            return_data = handler.run(conn, tmp, 'template', module_args, inject)
            if return_data.result.has_key('failed'):
                return return_data
            elif return_data.result['changed']:
                changed = True

        # Dirty service notification.
        if changed:
            cp = callback_plugins[0]
            handler_name = 'restart munin-node'
            cp.playbook._flag_handler(cp.play, template(cp.play.basedir, handler_name, cp.task.module_vars), inject['inventory_hostname'])

        result = dict()
        result['changed'] = changed
        if changed:
            result['msg'] = 'Munin plugin %s installed.' % name
        return ReturnData(conn=conn, comm_ok=True, result=result)

