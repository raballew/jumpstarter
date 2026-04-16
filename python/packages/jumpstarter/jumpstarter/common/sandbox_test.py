from jumpstarter.common.sandbox import SandboxPolicy


class TestSandboxPolicyDefaults:
    def test_enabled_defaults_to_false(self):
        policy = SandboxPolicy()
        assert policy.enabled is False

    def test_enabled_can_be_set_to_true(self):
        policy = SandboxPolicy(enabled=True)
        assert policy.enabled is True

    def test_enabled_can_be_set_to_false_explicitly(self):
        policy = SandboxPolicy(enabled=False)
        assert policy.enabled is False


class TestSandboxPolicyEquality:
    def test_two_default_policies_are_equal(self):
        assert SandboxPolicy() == SandboxPolicy()

    def test_enabled_policies_are_equal(self):
        assert SandboxPolicy(enabled=True) == SandboxPolicy(enabled=True)

    def test_different_enabled_values_are_not_equal(self):
        assert SandboxPolicy(enabled=True) != SandboxPolicy(enabled=False)
