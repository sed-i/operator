import os


class JujuContext:
    def __init__(self, context: dict):
        self.model = context.get("JUJU_MODEL_NAME")
        self.model_uuid = context.get("JUJU_MODEL_UUID")
        self.unit_name = context.get("JUJU_APP_NAME")
        self.app_name, self.unit_id = self.unit_name.split("/")
        self.juju_version = context.get("JUJU_VERSION")
        self.hook_name = context.get("JUJU_HOOK_NAME")


class InstallContext(JujuContext):
    pass


class LeaderElectedContext(JujuContext):
    pass


# Same for start, config-changed, update-status, stop, remove


class PebbleReadyContext(JujuContext):
    def __init__(self, context: dict):
        super().__init__(context)
        self.workload_name = context["JUJU_WORKLOAD_NAME"]


class RelationContext(JujuContext):
    def __init__(self, context: dict):
        super().__init__(context)
        self.relation_name = context["JUJU_RELATION"]
        self.remote_app_name = context["JUJU_REMOTE_APP"]
        self.relation_id = context["JUJU_RELATION_ID"].split(":")[1]

    @property
    def remote_app_data(self):
        return "hook_tools.relation_get(self.relation_id, self.remote_app_name, is_app=True)"

    @property
    def local_app_data(self):
        return "hook_tools.relation_get(self.relation_id, self.unit_name, is_app=True)"


class RelationCreatedContext(RelationContext):
    pass


class RelationJoinedContext(RelationContext):
    def __init__(self, context: dict):
        super().__init__(context)
        self.remote_unit_name = context["JUJU_REMOTE_UNIT"]

    @property
    def remote_unit_data(self):
        return "hook_tools.relation_get(self.relation_id, self.remote_unit_name, is_app=False)"


# Similar for the other events


def context_from_dict(env: dict) -> JujuContext:
    ctx = JujuContext(env)
    if ctx.hook_name == "install":
        return InstallContext(env)
    elif ctx.hook_name == "leader-elected":
        return LeaderElectedContext(env)
    elif ctx.hook_name == f"{env.get('JUJU_WORKLOAD_NAME')}-pebble-ready":
        return PebbleReadyContext(env)
    elif ctx.hook_name == f"{env.get('JUJU_RELATION')}-relation-created":
        return RelationCreatedContext(env)
    # etc.
    else:
        return ctx


def context_from_environ() -> JujuContext:
    return context_from_dict(dict(os.environ))


# Here's how a charm could look like:
if __name__ == "__main__":
    current_hook = context_from_environ()
    if isinstance(current_hook, PebbleReadyContext):
        print("pebble ready for", current_hook.workload_name)
