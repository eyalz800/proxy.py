import unittest
from unittest.mock import Mock
from proxy import proxy

class MyProxiedClass:
    def __init__(self, value):
        self.value = value

    def get_value(self):
        return self.value

class TestProxy(unittest.TestCase):

    def test_proxy_decorator_and_creation(self):
        @proxy(MyProxiedClass)
        class MyProxy(MyProxiedClass):
            def get_doubled_value(self):
                return proxy.get(MyProxiedClass, self).get_value() * 2

        proxied_instance = MyProxiedClass(10)
        proxy_instance = proxy.create(MyProxy, proxied_instance)

        self.assertIsInstance(proxy_instance, MyProxy)
        self.assertEqual(proxy_instance.get_doubled_value(), 20)
        self.assertEqual(proxy_instance.get_value(), 10) # Accessing proxied method
        self.assertEqual(proxy_instance.value, 10) # Accessing proxied value

    def test_proxy_set_value_distinct(self):
        @proxy(MyProxiedClass)
        class MyProxy(MyProxiedClass):
            def get_doubled_value(self):
                return proxy.get(MyProxiedClass, self).get_value() * 2

        proxied_instance = MyProxiedClass(10)
        proxy_instance = proxy.create(MyProxy, proxied_instance)

        self.assertEqual(proxy_instance.value, 10) # Accessing proxied value
        proxy_instance.value = 20  # Set a new value on the proxy
        self.assertEqual(proxy_instance.value, 20)  # Check the proxy's value
        self.assertEqual(proxied_instance.value, 10)  # Check the proxy's value
        proxied_instance.value = 30  # Change the proxied instance's value
        self.assertEqual(proxy_instance.value, 20)  # Check the proxy's value
        del proxy_instance.value
        self.assertEqual(proxy_instance.value, 30)  # Check the proxy's value

    def test_proxy_get_method(self):
        @proxy(MyProxiedClass)
        class AnotherProxy(MyProxiedClass):
            pass

        proxied_instance = MyProxiedClass(5)
        proxy_instance = proxy.create(AnotherProxy, proxied_instance)

        retrieved_proxied = proxy.get(MyProxiedClass, proxy_instance)
        self.assertIs(retrieved_proxied, proxied_instance)
        self.assertEqual(retrieved_proxied.get_value(), 5)
        self.assertEqual(retrieved_proxied.value, 5)

    def test_proxy_with_additional_init_args(self):
        class AnotherProxiedClass:
            def __init__(self, a, b):
                self.sum = a + b

        @proxy(AnotherProxiedClass)
        class ProxyWithExtraInit(AnotherProxiedClass):
            def __init__(self, *args, extra_arg=0, **kwargs):
                self.extra_arg = extra_arg

        proxied_instance = AnotherProxiedClass(2, 3)
        proxy_instance = proxy.create(ProxyWithExtraInit, proxied_instance, extra_arg=10)

        self.assertEqual(proxy_instance.sum, 5)
        self.assertEqual(proxy_instance.extra_arg, 10)

    def test_proxy_own_attribute(self):
        class ProxiedClassWithAttribute:
            def __init__(self, value):
                self.value = value

        @proxy(ProxiedClassWithAttribute)
        class ProxyClassWithOwnAttribute(ProxiedClassWithAttribute):
            def __init__(self, *args, **kwargs):
                self.proxy_specific_value = "proxy_value"
                self.value = "proxy_overridden_value" # This will be the proxy's own value

        proxied_instance = ProxiedClassWithAttribute("original_value")
        proxy_instance = proxy.create(ProxyClassWithOwnAttribute, proxied_instance)

        # Access the proxy's own attribute
        self.assertEqual(proxy_instance.proxy_specific_value, "proxy_value")
        # Access the proxy's overridden 'value' attribute
        self.assertEqual(proxy_instance.value, "proxy_overridden_value")

        # Access the proxied object's 'value' attribute using proxy.get
        original_proxied = proxy.get(ProxiedClassWithAttribute, proxy_instance)
        self.assertEqual(original_proxied.value, "original_value")

        # Assert that the proxy's 'value' is different from the proxied object's 'value'
        self.assertNotEqual(proxy_instance.value, original_proxied.value)

    def test_database_proxy_example(self):
        # Mock the Database class
        class MockDatabase:
            def connect(self) -> str:
                return ""

            def disconnect(self):
                pass

            def execute_query(self, query: str) -> str:
                return f"Result for '{query}'"

        mock_real_db_instance = Mock(spec=MockDatabase)
        mock_real_db_instance.connect.return_value = "Connected"
        mock_real_db_instance.execute_query.return_value = "Mocked Result"

        @proxy(MockDatabase)
        class MockDatabasePerformanceTracer(MockDatabase):
            def execute_query(self, query: str) -> str:
                # Simulate performance tracing logic without actual time measurements
                # We'll assert this method is called, and the underlying is also called
                return proxy.get(MockDatabase, self).execute_query(query)

        # Create the proxy instance
        db_proxy_instance = proxy.create(MockDatabasePerformanceTracer, mock_real_db_instance)

        # Test delegated methods (connect, disconnect)
        self.assertEqual(db_proxy_instance.connect(), "Connected")
        mock_real_db_instance.connect.assert_called_once()

        db_proxy_instance.disconnect()
        mock_real_db_instance.disconnect.assert_called_once()

        # Test overridden method (execute_query)
        # The proxy's execute_query should be called, which in turn calls the proxied object's execute_query
        result = db_proxy_instance.execute_query("SELECT * FROM users;")
        self.assertEqual(result, "Mocked Result")
        mock_real_db_instance.execute_query.assert_called_once_with("SELECT * FROM users;")

        # Verify that accessing the underlying object works
        retrieved_original = proxy.get(MockDatabase, db_proxy_instance)
        self.assertIs(retrieved_original, mock_real_db_instance)

    def test_proxy_class_dir_contains_proxied_members(self):
        class ProxiedForDirTest:
            CLASS_ATTR = "hello"

            def __init__(self, val):
                self.val = val

            def method_a(self):
                pass

            def method_b(self):
                pass

        @proxy(ProxiedForDirTest)
        class ProxyForDirTest(ProxiedForDirTest):
            def new_method_on_proxy(self):
                pass

        # Members of ProxiedForDirTest that should appear in the proxy's class dir
        expected_members = ['__init__', 'method_a', 'method_b', 'CLASS_ATTR', 'new_method_on_proxy']

        proxy_dir = dir(ProxyForDirTest)

        for member in expected_members:
            self.assertIn(member, proxy_dir, f"'{member}' not found in proxy class dir")

        # Also check some common dunder methods expected to be present due to proxy mechanism
        self.assertIn('__getattribute__', proxy_dir)
        self.assertIn('__setattr__', proxy_dir)
        self.assertIn('__delattr__', proxy_dir)

    def test_proxy_instance_dir_contains_proxied_members(self):
        class ProxiedForDirTest:
            CLASS_ATTR = "hello"

            def __init__(self, val):
                self.val = val

            def method_a(self):
                pass

            def method_b(self):
                pass

        @proxy(ProxiedForDirTest)
        class ProxyForDirTest(ProxiedForDirTest):
            def new_method_on_proxy(self):
                pass

        # Create an instance of the proxy class
        proxy_instance = proxy.create(ProxyForDirTest, ProxiedForDirTest(42))

        # Members of ProxiedForDirTest and ProxyForDirTest that should appear in the proxy instance's dir
        # This includes instance attributes, class attributes, and methods
        expected_members = ['__init__', 'method_a', 'method_b', 'CLASS_ATTR', 'new_method_on_proxy', 'val']

        instance_dir = dir(proxy_instance)

        for member in expected_members:
            self.assertIn(member, instance_dir, f"'{member}' not found in proxy instance dir")

        # Also check some common dunder methods expected to be present due to proxy mechanism
        self.assertIn('__getattribute__', instance_dir)
        self.assertIn('__setattr__', instance_dir)
        self.assertIn('__delattr__', instance_dir)

    def test_proxy_instance_dict_is_accessible(self):
        class ProxiedForDictTest:
            def __init__(self, name):
                self.name = name

        @proxy(ProxiedForDictTest)
        class ProxyForDictTest(ProxiedForDictTest):
            pass

        proxied_instance = ProxiedForDictTest("original")
        proxy_instance = proxy.create(ProxyForDictTest, proxied_instance)

        # 1. Check if __dict__ is accessible and is a dict
        self.assertIsInstance(proxy_instance.__dict__, dict)

        # 2. Add a new attribute to the proxy instance
        proxy_instance.new_proxy_attr = 123
        self.assertEqual(proxy_instance.new_proxy_attr, 123)

        # 3. Verify the new attribute is in the proxy's __dict__
        self.assertIn('new_proxy_attr', proxy_instance.__dict__)
        self.assertEqual(proxy_instance.__dict__['new_proxy_attr'], 123)

        # 4. Ensure setting an attribute on the proxy doesn't affect the proxied instance's __dict__
        self.assertNotIn('new_proxy_attr', proxied_instance.__dict__)
        self.assertIn('name', proxied_instance.__dict__)

        # Test setting an attribute that also exists on the proxied object, but as an own attribute of the proxy
        proxy_instance.name = "proxy_name"
        self.assertEqual(proxy_instance.name, "proxy_name")
        self.assertEqual(proxied_instance.name, "original") # Original should be unchanged
        self.assertIn('name', proxy_instance.__dict__) # 'name' should now be in proxy's dict
        self.assertEqual(proxy_instance.__dict__['name'], "proxy_name")


if __name__ == '__main__':
    unittest.main()
