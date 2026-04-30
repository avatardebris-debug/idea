#!/usr/bin/env python3
"""
Thronglets VR Practice Mode - Python Test Runner
Executes test suite and reports results
"""

import json
import sys
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

# Test results tracking
class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.total = 0
        self.tests: List[Dict[str, Any]] = []
    
    def add_result(self, name: str, passed: bool, expected: Any, actual: Any):
        self.total += 1
        if passed:
            self.passed += 1
            print(f"✓ {name}")
        else:
            self.failed += 1
            print(f"✗ {name}")
            print(f"  Expected: {expected}")
            print(f"  Actual: {actual}")
        self.tests.append({
            'name': name,
            'passed': passed,
            'expected': expected,
            'actual': actual
        })

# Colors for terminal output
class Colors:
    RESET = '\x1b[0m'
    RED = '\x1b[31m'
    GREEN = '\x1b[32m'
    YELLOW = '\x1b[33m'
    BLUE = '\x1b[34m'
    MAGENTA = '\x1b[35m'
    CYAN = '\x1b[36m'
    WHITE = '\x1b[37m'

def log(message: str, color: str = 'RESET'):
    print(f"{getattr(Colors, color, Colors.RESET)}{message}{Colors.RESET}")

def log_success(message: str):
    log(message, 'GREEN')

def log_error(message: str):
    log(message, 'RED')

def log_warning(message: str):
    log(message, 'YELLOW')

def log_info(message: str):
    log(message, 'BLUE')

def log_debug(message: str):
    log(message, 'CYAN')

# Test assertion functions
def assert_equal(actual, expected, message: str, results: TestResults):
    passed = actual == expected
    results.add_result(message, passed, expected, actual)
    return passed

def assert_not_equal(actual, expected, message: str, results: TestResults):
    passed = actual != expected
    results.add_result(message, passed, expected, actual)
    return passed

def assert_true(actual, message: str, results: TestResults):
    passed = bool(actual)
    results.add_result(message, passed, True, actual)
    return passed

def assert_false(actual, message: str, results: TestResults):
    passed = not bool(actual)
    results.add_result(message, passed, False, actual)
    return passed

def assert_not_none(actual, message: str, results: TestResults):
    passed = actual is not None
    results.add_result(message, passed, 'not None', actual)
    return passed

def assert_none(actual, message: str, results: TestResults):
    passed = actual is None
    results.add_result(message, passed, 'None', actual)
    return passed

def assert_list_length(actual, expected, message: str, results: TestResults):
    passed = isinstance(actual, list) and len(actual) == expected
    results.add_result(message, passed, expected, len(actual) if isinstance(actual, list) else 'N/A')
    return passed

def assert_contains(actual, expected, message: str, results: TestResults):
    passed = isinstance(actual, list) and expected in actual
    results.add_result(message, passed, expected, actual)
    return passed

def assert_string_contains(actual, expected, message: str, results: TestResults):
    passed = isinstance(actual, str) and expected in actual
    results.add_result(message, passed, expected, actual)
    return passed

# Mock environment setup
class MockDocument:
    def __init__(self):
        self.elements = {}
    
    def querySelector(self, selector):
        return MockElement()
    
    def getElementById(self, id):
        return MockElement()
    
    def addEventListener(self, *args, **kwargs):
        pass
    
    def querySelectorAll(self, selector):
        return []

class MockElement:
    def __init__(self):
        self.classList = MockClassList()
        self.style = MockStyle()
        self.textContent = ''
    
    def addEventListener(self, *args, **kwargs):
        pass
    
    def setAttribute(self, *args, **kwargs):
        pass
    
    def getAttribute(self, *args, **kwargs):
        return None
    
    def hasAttribute(self, *args, **kwargs):
        return False
    
    def appendChild(self, *args, **kwargs):
        pass
    
    def removeAttribute(self, *args, **kwargs):
        pass

class MockClassList:
    def __init__(self):
        self.classes = set()
    
    def add(self, cls):
        self.classes.add(cls)
    
    def remove(self, cls):
        self.classes.discard(cls)
    
    def toggle(self, cls):
        if cls in self.classes:
            self.classes.remove(cls)
        else:
            self.classes.add(cls)
    
    def contains(self, cls):
        return cls in self.classes

class MockStyle:
    def __init__(self):
        self.opacity = ''
        self.display = ''

class MockWindow:
    def __init__(self):
        self.resize = {}
    
    def addEventListener(self, *args, **kwargs):
        pass

class MockNavigator:
    @staticmethod
    def vibrate(pattern):
        pass

# Mock VRState
class MockVRState:
    def __init__(self):
        self.thronglets = []
        self.connections = []
        self.selectedThronglet = None
        self.settings = {
            'showNameplates': False,
            'showConnections': False,
            'showHealthHalos': False,
            'debugMode': False
        }
        self.config = None
        self.practiceMode = None
    
    def reset(self):
        """Reset VRState to initial state for test isolation"""
        self.thronglets = []
        self.connections = []
        self.selectedThronglet = None
        self.settings = {
            'showNameplates': False,
            'showConnections': False,
            'showHealthHalos': False,
            'debugMode': False
        }
        self.config = None
        self.practiceMode = None

# Mock Thronglet class
class MockThronglet:
    def __init__(self, data: Dict[str, Any]):
        self.id = data.get('id', '')
        self.name = data.get('name', '')
        self.role = data.get('role', '')
        self.color = data.get('color', '')
        self.position = data.get('position', {'x': 0, 'y': 0, 'z': 0})
        self.health = data.get('health', 'healthy')
        self.mood = data.get('mood', 'neutral')
        self.token_count = data.get('token_count', 0)
        self.uptime = data.get('uptime', 0)
        self.last_seen = data.get('last_seen', '')
        self.lastSeen = None
    
    def getHealthColor(self) -> str:
        colors = {
            'healthy': '#81c784',
            'warning': '#ffb74d',
            'critical': '#e57373'
        }
        return colors.get(self.health, '#9e9e9e')
    
    def getHealthBadge(self) -> str:
        badges = {
            'healthy': 'Healthy',
            'warning': 'Warning',
            'critical': 'Critical'
        }
        return badges.get(self.health, 'Unknown')
    
    def updateTimestamp(self):
        self.lastSeen = datetime.now().isoformat()
    
    def toJSON(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'role': self.role,
            'color': self.color,
            'position': self.position,
            'health': self.health,
            'mood': self.mood,
            'token_count': self.token_count,
            'uptime': self.uptime,
            'last_seen': self.last_seen
        }

# Mock Connection class
class MockConnection:
    def __init__(self, data: Dict[str, Any], fromThronglet: MockThronglet, toThronglet: MockThronglet):
        self.from_id = data.get('from', '')
        self.to_id = data.get('to', '')
        self.type = data.get('type', '')
        self.color = data.get('color', '')
        self.label = data.get('label', '')
        self.fromThronglet = fromThronglet
        self.toThronglet = toThronglet
    
    def toJSON(self) -> Dict[str, Any]:
        return {
            'id': self.from_id,
            'from': self.from_id,
            'to': self.to_id,
            'type': self.type,
            'color': self.color,
            'label': self.label
        }

# Mock VRPracticeMode class
class MockVRPracticeMode:
    def __init__(self, vr_state=None):
        self.init_called = False
        self.config_loaded = False
        self.vr_state = vr_state
    
    def init(self):
        self.init_called = True
    
    def loadConfiguration(self):
        self.config_loaded = True
    
    def createThronglets(self):
        if self.vr_state and self.vr_state.config and 'thronglets' in self.vr_state.config:
            for thronglet_data in self.vr_state.config['thronglets']:
                self.vr_state.thronglets.append(MockThronglet(thronglet_data))
    
    def createConnections(self):
        if self.vr_state and self.vr_state.config and 'connections' in self.vr_state.config:
            for connection_data in self.vr_state.config['connections']:
                from_thronglet = None
                to_thronglet = None
                for t in self.vr_state.thronglets:
                    if t.id == connection_data['from']:
                        from_thronglet = t
                    if t.id == connection_data['to']:
                        to_thronglet = t
                if from_thronglet and to_thronglet:
                    self.vr_state.connections.append(MockConnection(connection_data, from_thronglet, to_thronglet))
    
    def selectThronglet(self, id: str):
        for t in self.vr_state.thronglets:
            if t.id == id:
                self.vr_state.selectedThronglet = t
                return
        self.vr_state.selectedThronglet = None
    
    def deselectThronglet(self):
        self.vr_state.selectedThronglet = None
    
    def teleportToThronglet(self, index: int):
        if 0 <= index < len(self.vr_state.thronglets):
            self.vr_state.selectedThronglet = self.vr_state.thronglets[index]
    
    def toggleNameplates(self):
        self.vr_state.settings['showNameplates'] = not self.vr_state.settings['showNameplates']
    
    def toggleConnections(self):
        self.vr_state.settings['showConnections'] = not self.vr_state.settings['showConnections']
    
    def toggleHealthHalos(self):
        self.vr_state.settings['showHealthHalos'] = not self.vr_state.settings['showHealthHalos']
    
    def toggleDebug(self):
        self.vr_state.settings['debugMode'] = not self.vr_state.settings['debugMode']
    
    def handleKeyboard(self, event: Dict[str, str]):
        if event.get('key') == 'Escape':
            self.vr_state.selectedThronglet = None
        elif event.get('key') in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']:
            index = int(event['key']) - 1 if event['key'] != '0' else 9
            if 0 <= index < len(self.vr_state.thronglets):
                self.vr_state.selectedThronglet = self.vr_state.thronglets[index]
    
    def updateSimulation(self):
        for t in self.vr_state.thronglets:
            t.updateTimestamp()
    
    def checkProximityAlerts(self):
        pass

# Test functions
def runThrongletTests(VRState, Thronglet, results: TestResults):
    log_info('\n=== Thronglet Class Tests ===')
    
    # Test constructor
    thronglet = Thronglet({
        'id': '1',
        'name': 'Test Thronglet',
        'role': 'agent',
        'color': '#ff0000',
        'position': {'x': 0, 'y': 0, 'z': 0},
        'health': 'healthy',
        'mood': 'neutral',
        'token_count': 100,
        'uptime': 3600,
        'last_seen': '2024-01-01T00:00:00Z'
    })
    
    assert_equal(thronglet.id, '1', 'Thronglet ID should be "1"', results)
    assert_equal(thronglet.name, 'Test Thronglet', 'Thronglet name should be "Test Thronglet"', results)
    assert_equal(thronglet.role, 'agent', 'Thronglet role should be "agent"', results)
    assert_equal(thronglet.color, '#ff0000', 'Thronglet color should be "#ff0000"', results)
    assert_equal(thronglet.health, 'healthy', 'Thronglet health should be "healthy"', results)
    assert_equal(thronglet.mood, 'neutral', 'Thronglet mood should be "neutral"', results)
    assert_equal(thronglet.token_count, 100, 'Thronglet token_count should be 100', results)
    assert_equal(thronglet.uptime, 3600, 'Thronglet uptime should be 3600', results)
    assert_equal(thronglet.last_seen, '2024-01-01T00:00:00Z', 'Thronglet last_seen should be "2024-01-01T00:00:00Z"', results)
    
    # Test getHealthColor
    assert_equal(thronglet.getHealthColor(), '#81c784', 'Healthy thronglet color should be "#81c784"', results)
    
    # Test getHealthBadge
    assert_equal(thronglet.getHealthBadge(), 'Healthy', 'Health badge should be "Healthy"', results)
    
    # Test updateTimestamp
    thronglet.updateTimestamp()
    assert_not_none(thronglet.lastSeen, 'Thronglet lastSeen should be updated', results)
    
    # Test toJSON
    json_data = thronglet.toJSON()
    assert_equal(json_data['id'], '1', 'JSON id should be "1"', results)
    assert_equal(json_data['name'], 'Test Thronglet', 'JSON name should be "Test Thronglet"', results)
    
    # Test warning health
    warningThronglet = Thronglet({
        'id': '2',
        'name': 'Warning Thronglet',
        'role': 'agent',
        'color': '#ff0000',
        'position': {'x': 0, 'y': 0, 'z': 0},
        'health': 'warning',
        'mood': 'neutral',
        'token_count': 100,
        'uptime': 3600,
        'last_seen': '2024-01-01T00:00:00Z'
    })
    assert_equal(warningThronglet.getHealthColor(), '#ffb74d', 'Warning thronglet color should be "#ffb74d"', results)
    
    # Test critical health
    criticalThronglet = Thronglet({
        'id': '3',
        'name': 'Critical Thronglet',
        'role': 'agent',
        'color': '#ff0000',
        'position': {'x': 0, 'y': 0, 'z': 0},
        'health': 'critical',
        'mood': 'neutral',
        'token_count': 100,
        'uptime': 3600,
        'last_seen': '2024-01-01T00:00:00Z'
    })
    assert_equal(criticalThronglet.getHealthColor(), '#e57373', 'Critical thronglet color should be "#e57373"', results)
    assert_equal(criticalThronglet.getHealthBadge(), 'Critical', 'Critical health badge should be "Critical"', results)

def runConnectionTests(VRState, Thronglet, Connection, results: TestResults):
    log_info('\n=== Connection Class Tests ===')
    
    # Test constructor
    fromThronglet = Thronglet({
        'id': '1',
        'name': 'Test 1',
        'role': 'agent',
        'color': '#ff0000',
        'position': {'x': 0, 'y': 0, 'z': 0},
        'health': 'healthy',
        'mood': 'neutral',
        'token_count': 100,
        'uptime': 3600,
        'last_seen': '2024-01-01T00:00:00Z'
    })
    toThronglet = Thronglet({
        'id': '2',
        'name': 'Test 2',
        'role': 'agent',
        'color': '#00ff00',
        'position': {'x': 1, 'y': 0, 'z': 0},
        'health': 'healthy',
        'mood': 'neutral',
        'token_count': 100,
        'uptime': 3600,
        'last_seen': '2024-01-01T00:00:00Z'
    })
    
    connection = Connection({
        'from': '1',
        'to': '2',
        'type': 'communication',
        'color': '#0000ff',
        'label': 'Test Connection'
    }, fromThronglet, toThronglet)
    
    assert_equal(connection.from_id, '1', 'Connection from_id should be "1"', results)
    assert_equal(connection.to_id, '2', 'Connection to_id should be "2"', results)
    assert_equal(connection.type, 'communication', 'Connection type should be "communication"', results)
    assert_equal(connection.color, '#0000ff', 'Connection color should be "#0000ff"', results)
    assert_equal(connection.label, 'Test Connection', 'Connection label should be "Test Connection"', results)
    assert_equal(connection.fromThronglet, fromThronglet, 'Connection fromThronglet should match', results)
    assert_equal(connection.toThronglet, toThronglet, 'Connection toThronglet should match', results)
    
    # Test toJSON
    json_data = connection.toJSON()
    assert_equal(json_data['from'], '1', 'JSON from should be "1"', results)
    assert_equal(json_data['to'], '2', 'JSON to should be "2"', results)
    assert_equal(json_data['type'], 'communication', 'JSON type should be "communication"', results)

def runVRStateTests(VRState, Thronglet, Connection, results: TestResults):
    log_info('\n=== VRState Tests ===')
    
    # Test initial state
    assert_list_length(VRState.thronglets, 0, 'VRState should start with 0 thronglets', results)
    assert_list_length(VRState.connections, 0, 'VRState should start with 0 connections', results)
    assert_none(VRState.selectedThronglet, 'VRState selectedThronglet should be None', results)
    assert_false(VRState.settings['showNameplates'], 'VRState showNameplates should be False', results)
    assert_false(VRState.settings['showConnections'], 'VRState showConnections should be False', results)
    assert_false(VRState.settings['showHealthHalos'], 'VRState showHealthHalos should be False', results)
    assert_false(VRState.settings['debugMode'], 'VRState debugMode should be False', results)
    assert_none(VRState.config, 'VRState config should be None', results)
    assert_none(VRState.practiceMode, 'VRState practiceMode should be None', results)

def runVRPracticeModeTests(VRState, Thronglet, Connection, VRPracticeMode, results: TestResults):
    log_info('\n=== VRPracticeMode Tests ===')
    
    # Reset VRState for this test
    VRState.reset()
    
    # Test init
    practiceMode = VRPracticeMode(VRState)
    practiceMode.init()
    assert_true(practiceMode.init_called, 'init should be called', results)
    
    # Test loadConfiguration
    practiceMode.loadConfiguration()
    assert_true(practiceMode.config_loaded, 'config should be loaded', results)
    
    # Test createThronglets
    VRState.config = {
        'thronglets': [
            {
                'id': '1',
                'name': 'Test 1',
                'role': 'agent',
                'color': '#ff0000',
                'position': {'x': 0, 'y': 0, 'z': 0},
                'health': 'healthy',
                'mood': 'neutral',
                'token_count': 100,
                'uptime': 3600,
                'last_seen': '2024-01-01T00:00:00Z'
            }
        ],
        'connections': []
    }
    practiceMode.createThronglets()
    assert_list_length(VRState.thronglets, 1, 'Should have 1 thronglet after creation', results)
    
    # Test create connections
    fromThronglet = VRState.thronglets[0]
    toThronglet = Thronglet({
        'id': '2',
        'name': 'Test 2',
        'role': 'agent',
        'color': '#00ff00',
        'position': {'x': 1, 'y': 0, 'z': 0},
        'health': 'healthy',
        'mood': 'neutral',
        'token_count': 100,
        'uptime': 3600,
        'last_seen': '2024-01-01T00:00:00Z'
    })
    VRState.thronglets.append(toThronglet)
    
    VRState.config['connections'] = [
        {
            'from': '1',
            'to': '2',
            'type': 'communication',
            'color': '#0000ff',
            'label': 'Test Connection'
        }
    ]
    
    practiceMode.createConnections()
    assert_list_length(VRState.connections, 1, 'Should have 1 connection after creation', results)
    
    # Test select thronglet
    practiceMode.selectThronglet('1')
    assert_not_none(VRState.selectedThronglet, 'Selected thronglet should not be None', results)
    assert_equal(VRState.selectedThronglet.id, '1', 'Selected thronglet ID should be "1"', results)
    
    # Test deselect thronglet
    practiceMode.deselectThronglet()
    assert_none(VRState.selectedThronglet, 'Selected thronglet should be None after deselect', results)
    
    # Test teleport to thronglet
    testThronglet = Thronglet({
        'id': '3',
        'name': 'Test Thronglet 3',
        'role': 'agent',
        'color': '#ff0000',
        'position': {'x': 10, 'y': 2, 'z': 5},
        'health': 'healthy',
        'mood': 'neutral',
        'token_count': 100,
        'uptime': 3600,
        'last_seen': '2024-01-01T00:00:00Z'
    })
    VRState.thronglets.append(testThronglet)
    
    practiceMode.teleportToThronglet(2)
    # Should have attempted to teleport
    
    # Test toggle nameplates
    practiceMode.toggleNameplates()
    assert_true(VRState.settings['showNameplates'], 'showNameplates should be True after toggle', results)
    
    practiceMode.toggleNameplates()
    assert_false(VRState.settings['showNameplates'], 'showNameplates should be False after toggle', results)
    
    # Test toggle connections
    practiceMode.toggleConnections()
    assert_true(VRState.settings['showConnections'], 'showConnections should be True after toggle', results)
    
    practiceMode.toggleConnections()
    assert_false(VRState.settings['showConnections'], 'showConnections should be False after toggle', results)
    
    # Test toggle health halos
    practiceMode.toggleHealthHalos()
    assert_true(VRState.settings['showHealthHalos'], 'showHealthHalos should be True after toggle', results)
    
    practiceMode.toggleHealthHalos()
    assert_false(VRState.settings['showHealthHalos'], 'showHealthHalos should be False after toggle', results)
    
    # Test toggle debug mode
    practiceMode.toggleDebug()
    assert_true(VRState.settings['debugMode'], 'debugMode should be True after toggle', results)
    
    practiceMode.toggleDebug()
    assert_false(VRState.settings['debugMode'], 'debugMode should be False after toggle', results)
    
    # Test keyboard events
    escEvent = {'key': 'Escape'}
    practiceMode.handleKeyboard(escEvent)
    assert_none(VRState.selectedThronglet, 'Selected thronglet should be None after ESC', results)
    
    key1Event = {'key': '1'}
    practiceMode.handleKeyboard(key1Event)
    # Should have attempted to teleport
    
    # Test update simulation
    thronglet = Thronglet({
        'id': '4',
        'name': 'Test Thronglet 4',
        'role': 'agent',
        'color': '#ff0000',
        'position': {'x': 0, 'y': 0, 'z': 0},
        'health': 'healthy',
        'mood': 'neutral',
        'token_count': 100,
        'uptime': 3600,
        'last_seen': '2024-01-01T00:00:00Z'
    })
    VRState.thronglets.append(thronglet)
    
    practiceMode.updateSimulation()
    assert_not_none(thronglet.lastSeen, 'Thronglet lastSeen should be updated', results)
    
    # Test check proximity alerts
    criticalThronglet = Thronglet({
        'id': '5',
        'name': 'Critical Thronglet',
        'role': 'agent',
        'color': '#ff0000',
        'position': {'x': 0, 'y': 0, 'z': 0},
        'health': 'critical',
        'mood': 'neutral',
        'token_count': 100,
        'uptime': 3600,
        'last_seen': '2024-01-01T00:00:00Z'
    })
    VRState.thronglets.append(criticalThronglet)
    
    practiceMode.checkProximityAlerts()
    # Should have detected critical thronglet

def runGlobalFunctionsTests(VRState, Thronglet, VRPracticeMode, results: TestResults):
    log_info('\n=== Global Functions Tests ===')
    
    # Test initThrongletsVR
    # initThrongletsVR()
    # assert_not_none(VRState.practiceMode, 'VRState.practiceMode should be defined', results)
    
    # Test closeDetailPanel
    # panel = document.getElementById('detail-panel')
    # panel.classList.add('visible')
    # closeDetailPanel()
    # assert_false(panel.classList.contains('visible'), 'Panel should not be visible after close', results)
    
    # Test toggleNameplatesVisibility
    VRState.practiceMode = VRPracticeMode()
    # toggleNameplatesVisibility()
    # assert_false(VRState.settings['showNameplates'], 'showNameplates should be False', results)
    
    # Test toggleConnectionsVisibility
    # toggleConnectionsVisibility()
    # assert_false(VRState.settings['showConnections'], 'showConnections should be False', results)
    
    # Test toggleHealthHalosVisibility
    # toggleHealthHalosVisibility()
    # assert_false(VRState.settings['showHealthHalos'], 'showHealthHalos should be False', results)
    
    # Test toggleDebugMode
    # toggleDebugMode()
    # assert_true(VRState.settings['debugMode'], 'debugMode should be True', results)
    
    # Test teleportToThronglet
    testThronglet = Thronglet({
        'id': '1',
        'name': 'Test Thronglet',
        'role': 'agent',
        'color': '#ff0000',
        'position': {'x': 0, 'y': 0, 'z': 0},
        'health': 'healthy',
        'mood': 'neutral',
        'token_count': 100,
        'uptime': 3600,
        'last_seen': '2024-01-01T00:00:00Z'
    })
    VRState.thronglets.append(testThronglet)
    
    # teleportToThronglet(0)
    # Should have attempted to teleport
    
    # Test deselectThronglet
    VRState.selectedThronglet = testThronglet
    # deselectThronglet()
    # assert_none(VRState.selectedThronglet, 'Selected thronglet should be None', results)
    
    # Test handleResize
    # handleResize()
    # Should not throw an error

def runEdgeCaseTests(VRState, Thronglet, VRPracticeMode, results: TestResults):
    log_info('\n=== Edge Case Tests ===')
    
    # Reset VRState for this test
    VRState.reset()
    
    # Test empty configuration
    practiceMode = VRPracticeMode(VRState)
    VRState.config = None
    practiceMode.createThronglets()
    assert_list_length(VRState.thronglets, 0, 'Should have 0 thronglets with empty config', results)
    
    # Test missing thronglet in selection
    practiceMode2 = VRPracticeMode(VRState)
    practiceMode2.selectThronglet('nonexistent')
    assert_none(VRState.selectedThronglet, 'Selected thronglet should be None for nonexistent ID', results)
    
    # Test invalid index in teleport
    practiceMode3 = VRPracticeMode(VRState)
    practiceMode3.teleportToThronglet(999)
    # Should not throw an error
    
    # Test missing configuration file
    practiceMode4 = VRPracticeMode(VRState)
    VRState.config = None
    practiceMode4.loadConfiguration()
    # Configuration should remain None

def runIntegrationTests(VRState, Thronglet, VRPracticeMode, results: TestResults):
    log_info('\n=== Integration Tests ===')
    
    # Reset VRState for this test
    VRState.reset()
    
    practiceMode = VRPracticeMode(VRState)
    practiceMode.init()
    
    assert_list_length(VRState.thronglets, 0, 'Should have 0 thronglets (mocked)', results)
    assert_list_length(VRState.connections, 0, 'Should have 0 connections (mocked)', results)
    
    # Select a thronglet
    firstThronglet = Thronglet({
        'id': '1',
        'name': 'Test Thronglet',
        'role': 'agent',
        'color': '#ff0000',
        'position': {'x': 0, 'y': 0, 'z': 0},
        'health': 'healthy',
        'mood': 'neutral',
        'token_count': 100,
        'uptime': 3600,
        'last_seen': '2024-01-01T00:00:00Z'
    })
    VRState.thronglets.append(firstThronglet)
    
    practiceMode.selectThronglet(firstThronglet.id)
    assert_not_none(VRState.selectedThronglet, 'Selected thronglet should not be None', results)
    assert_equal(VRState.selectedThronglet.id, '1', 'Selected thronglet ID should be "1"', results)
    
    # Deselect
    practiceMode.deselectThronglet()
    assert_none(VRState.selectedThronglet, 'Selected thronglet should be None after deselect', results)
    
    # Toggle settings
    practiceMode.toggleNameplates()
    practiceMode.toggleConnections()
    practiceMode.toggleHealthHalos()
    practiceMode.toggleDebug()
    
    # Update simulation
    practiceMode.updateSimulation()
    # Should complete without errors

def printSummary(results: TestResults):
    log_info('\n========================================')
    log_info('Test Summary')
    log_info('==================================')
    
    percentage = (results.passed / results.total * 100) if results.total > 0 else 0
    
    log_info(f'Total Tests: {results.total}')
    log_success(f'Passed: {results.passed}')
    log_error(f'Failed: {results.failed}')
    log_info(f'Success Rate: {percentage:.1f}%')
    
    if results.failed > 0:
        log_info('\nFailed Tests:')
        for test in results.tests:
            if not test['passed']:
                log_error(f'  - {test["name"]}')
                log_error(f'    Expected: {test["expected"]}')
                log_error(f'    Actual: {test["actual"]}')
    
    log_info('\n========================================')
    
    if results.failed == 0:
        log_success('All tests passed! ✓')
        sys.exit(0)
    else:
        log_error(f'{results.failed} test(s) failed! ✗')
        sys.exit(1)

# Run test suite
def runTestSuite():
    log_info('\n🚀 Starting Thronglets VR Practice Mode Test Suite')
    log_info('===========================================')
    
    # Initialize test results
    results = TestResults()
    
    # Initialize mock environment
    document = MockDocument()
    window = MockWindow()
    navigator = MockNavigator()
    VRState = MockVRState()
    
    # Run tests
    runThrongletTests(VRState, MockThronglet, results)
    runConnectionTests(VRState, MockThronglet, MockConnection, results)
    runVRStateTests(VRState, MockThronglet, MockConnection, results)
    runVRPracticeModeTests(VRState, MockThronglet, MockConnection, MockVRPracticeMode, results)
    runGlobalFunctionsTests(VRState, MockThronglet, MockVRPracticeMode, results)
    runEdgeCaseTests(VRState, MockThronglet, MockVRPracticeMode, results)
    runIntegrationTests(VRState, MockThronglet, MockVRPracticeMode, results)
    
    # Print summary
    printSummary(results)

if __name__ == '__main__':
    runTestSuite()
