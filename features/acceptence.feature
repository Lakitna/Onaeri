Feature: You can change the lamp using the tradfri remote
  As a user
  I want to be able to change the lamp using the remote
  In order to have control over the lamp.

  Scenario Outline: The user changes the brightness or color of a lamp
    Given there is a lamp
      And the lamp is turned on
    When the <attribute> of the lamp is changed
    Then the change will be detected

    Examples: Lamp attributes
      | attribute  |
      | brightness |
      | color      |


  Scenario: The user changes the brightness of multiple lamps
    Given there are 5 lamps
      And the lamps are turned on
    When the brightness of the lamps are changed
    Then the change will be detected

  Scenario: tst
    Given there are 2 lamp groups with 4 lamps each
      And the lamps are turned on
    When the brightness of the lamps are changed
    Then the change will be detected
