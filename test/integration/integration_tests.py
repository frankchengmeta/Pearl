#!/usr/bin/env fbpython
# (c) Meta Platforms, Inc. and affiliates. Confidential and proprietary.
import unittest

from pearl.core.common.neural_networks.value_networks import DuelingQValueNetwork

from pearl.core.common.pearl_agent import PearlAgent

from pearl.core.common.policy_learners.exploration_module.normal_distribution_exploration import (
    NormalDistributionExploration,
)
from pearl.core.common.replay_buffer.fifo_off_policy_replay_buffer import (
    FIFOOffPolicyReplayBuffer,
)
from pearl.core.common.replay_buffer.fifo_on_policy_replay_buffer import (
    FIFOOnPolicyReplayBuffer,
)
from pearl.core.common.replay_buffer.on_policy_episodic_replay_buffer import (
    OnPolicyEpisodicReplayBuffer,
)
from pearl.core.sequential_decision_making.policy_learners.ddpg import (
    DeepDeterministicPolicyGradient,
)

from pearl.core.sequential_decision_making.policy_learners.deep_q_learning import (
    DeepQLearning,
)

from pearl.core.sequential_decision_making.policy_learners.deep_sarsa import DeepSARSA
from pearl.core.sequential_decision_making.policy_learners.double_dqn import DoubleDQN
from pearl.core.sequential_decision_making.policy_learners.policy_gradient import (
    PolicyGradient,
)
from pearl.core.sequential_decision_making.policy_learners.ppo import (
    ProximalPolicyOptimization,
)
from pearl.core.sequential_decision_making.policy_learners.soft_actor_critic import (
    SoftActorCritic,
)
from pearl.core.sequential_decision_making.policy_learners.td3 import TD3

from pearl.gym.gym_environment import GymEnvironment
from pearl.online_learning.offline_learning_and_evaluation import (
    offline_evaluation,
    offline_learning,
)
from pearl.online_learning.online_learning import target_return_is_reached
from pearl.utils.set_seed import set_seed


class IntegrationTests(unittest.TestCase):
    """
    These tests may take a long time to run.
    """

    def test_dqn(self) -> None:
        """
        This test is checking if DQN will eventually get to 500 return for CartPole-v1
        """
        env = GymEnvironment("CartPole-v1")
        agent = PearlAgent(
            policy_learner=DeepQLearning(
                env.observation_space.shape[0],
                env.action_space,
                [64, 64],
                training_rounds=20,
            ),
            replay_buffer=FIFOOffPolicyReplayBuffer(10_000),
        )
        self.assertTrue(
            target_return_is_reached(
                target_return=500,
                max_episodes=1000,
                agent=agent,
                env=env,
                learn=True,
                learn_after_episode=True,
                exploit=False,
            )
        )

    # def test_dqn_on_frozen_lake(self) -> None:
    #     """
    #     This test is checking if DQN will eventually solve FrozenLake-v1
    #     whose observations need to be wrapped in a one-hot representation.
    #     """
    #     # TODO: flaky: sometimes not even 5,000 episodes is enough for learning
    #     # Need to debug.
    #
    #     environment = OneHotObservationsFromDiscrete(
    #         GymEnvironment("FrozenLake-v1", is_slippery=False)
    #     )
    #     state_dim = environment.observation_space.shape[0]
    #     agent = PearlAgent(
    #         policy_learner=DeepQLearning(
    #             state_dim=state_dim,
    #             action_space=environment.action_space,
    #             hidden_dims=[state_dim // 2, state_dim // 2],
    #             training_rounds=40,
    #         ),
    #         replay_buffer=FIFOOffPolicyReplayBuffer(1000),
    #     )

    #     self.assertTrue(
    #         target_return_is_reached(
    #             target_return=1.0,
    #             required_target_returns_in_a_row=5,
    #             max_episodes=1000,
    #             agent=agent,
    #             env=environment,
    #             learn=True,
    #             learn_after_episode=True,
    #             exploit=False,
    #         )
    #     )

    def test_double_dqn(self) -> None:
        """
        This test is checking if double DQN will eventually get to 500 return for CartPole-v1
        """
        env = GymEnvironment("CartPole-v1")
        agent = PearlAgent(
            policy_learner=DoubleDQN(
                env.observation_space.shape[0],
                env.action_space,
                [64, 64],
                training_rounds=20,
            ),
            replay_buffer=FIFOOffPolicyReplayBuffer(10_000),
        )
        self.assertTrue(
            target_return_is_reached(
                target_return=500,
                max_episodes=1000,
                agent=agent,
                env=env,
                learn=True,
                learn_after_episode=True,
                exploit=False,
            )
        )

    def test_sarsa(self) -> None:
        """
        This test is checking if SARSA will eventually get to 500 return for CartPole-v1
        Also use network instance to specify Q network
        """
        env = GymEnvironment("CartPole-v1")
        agent = PearlAgent(
            policy_learner=DeepSARSA(
                env.observation_space.shape[0],
                env.action_space,
                [64, 64],
                training_rounds=20,
            ),
            replay_buffer=FIFOOnPolicyReplayBuffer(10_000),
        )
        self.assertTrue(
            target_return_is_reached(
                target_return=500,
                max_episodes=1000,
                agent=agent,
                env=env,
                learn=True,
                learn_after_episode=True,
                exploit=False,
            )
        )

    def test_pg(self) -> None:
        """
        This test is checking if Policy Gradient will eventually get to 500 return for CartPole-v1
        """
        env = GymEnvironment("CartPole-v1")
        agent = PearlAgent(
            policy_learner=PolicyGradient(
                env.observation_space.shape[0],
                env.action_space,
                [64, 64],
                batch_size=500,
            ),
            replay_buffer=OnPolicyEpisodicReplayBuffer(10_000),
        )
        self.assertTrue(
            target_return_is_reached(
                target_return=500,
                max_episodes=10_000,
                agent=agent,
                env=env,
                learn=True,
                learn_after_episode=True,
                exploit=False,
            )
        )

    def test_dueling_dqn(
        self,
        batch_size: int = 128,
    ) -> None:
        env = GymEnvironment("CartPole-v1")
        q_network = DuelingQValueNetwork(
            state_dim=env.observation_space.shape[0],
            action_dim=env.action_space.n,
            hidden_dims=[64],
            output_dim=1,
        )
        agent = PearlAgent(
            policy_learner=DeepQLearning(
                env.observation_space.shape[0],
                env.action_space,
                training_rounds=20,
                network_instance=q_network,
                batch_size=batch_size,
            ),
            replay_buffer=FIFOOffPolicyReplayBuffer(10_000),
        )
        self.assertTrue(
            target_return_is_reached(
                agent=agent,
                env=env,
                target_return=500,
                max_episodes=10_000,
                learn=True,
                learn_after_episode=True,
                exploit=False,
            )
        )

    def test_ppo(self) -> None:
        """
        This test is checking if PPO using cumulated returns will eventually get to 500 return for CartPole-v1
        """
        env = GymEnvironment("CartPole-v1")
        agent = PearlAgent(
            policy_learner=ProximalPolicyOptimization(
                env.observation_space.shape[0],
                env.action_space,
                [64, 64],
                training_rounds=50,
                batch_size=64,
                epsilon=0.1,
            ),
            replay_buffer=OnPolicyEpisodicReplayBuffer(10_000),
        )
        self.assertTrue(
            target_return_is_reached(
                agent=agent,
                env=env,
                target_return=500,
                max_episodes=1000,
                learn=True,
                learn_after_episode=True,
                exploit=False,
            )
        )

    def test_sac(self) -> None:
        """
        This test is checking if SAC will eventually get to 500 return for CartPole-v1
        """
        env = GymEnvironment("CartPole-v1")
        agent = PearlAgent(
            policy_learner=SoftActorCritic(
                env.observation_space.shape[0],
                env.action_space,
                [64, 64],
                training_rounds=100,
                batch_size=100,
                entropy_coef=0.1,
                learning_rate=0.0003,
            ),
            replay_buffer=FIFOOffPolicyReplayBuffer(50000),
        )
        self.assertTrue(
            target_return_is_reached(
                agent=agent,
                env=env,
                target_return=500,
                max_episodes=10_000,
                learn=True,
                learn_after_episode=True,
                exploit=False,
            )
        )

    def test_cql(self) -> None:
        """
        This test is checking if DQN with conservative loss will eventually get to 500 return for CartPole-v1
        when training online. This is a dummy test for now as we don't expect to use conservative losses
        with online training. Will change this to an offline test when integrated with offline testing pipeline.
        """

        env = GymEnvironment("CartPole-v1")
        agent = PearlAgent(
            policy_learner=DeepQLearning(
                state_dim=env.observation_space.shape[0],
                action_space=env.action_space,
                hidden_dims=[64, 64],
                training_rounds=20,
                is_conservative=True,
            ),
            replay_buffer=FIFOOffPolicyReplayBuffer(10_000),
        )
        self.assertTrue(
            target_return_is_reached(
                target_return=500,
                max_episodes=1000,
                agent=agent,
                env=env,
                learn=True,
                learn_after_episode=True,
                exploit=False,
            )
        )

    def test_ddpg(self) -> None:
        """
        This test is checking if DDPG will eventually learn on Pendulum-v1
        If learns well, return will converge above -250
        Due to randomness in games, we check on moving avarage of episode returns
        """
        env = GymEnvironment("Pendulum-v1")
        agent = PearlAgent(
            policy_learner=DeepDeterministicPolicyGradient(
                state_dim=env.observation_space.shape[0],
                action_dim=env.action_space.shape[0],
                hidden_dims=[400, 300],
                exploration_module=NormalDistributionExploration(
                    mean=0, std_dev=0.2, max_action_value=2, min_action_value=-2
                ),
            ),
            replay_buffer=FIFOOffPolicyReplayBuffer(50000),
        )
        self.assertTrue(
            target_return_is_reached(
                agent=agent,
                env=env,
                target_return=-250,
                max_episodes=1000,
                learn=True,
                learn_after_episode=True,
                exploit=False,
                check_moving_average=True,
            )
        )

    def test_td3(self) -> None:
        """
        This test is checking if TD3 will eventually learn on Pendulum-v1
        If learns well, return will converge above -250
        Due to randomness in games, we check on moving avarage of episode returns
        """
        env = GymEnvironment("Pendulum-v1")
        agent = PearlAgent(
            policy_learner=TD3(
                state_dim=env.observation_space.shape[0],
                action_dim=env.action_space.shape[0],
                hidden_dims=[400, 300],
                exploration_module=NormalDistributionExploration(
                    mean=0, std_dev=0.2, max_action_value=2, min_action_value=-2
                ),
            ),
            replay_buffer=FIFOOffPolicyReplayBuffer(50000),
        )
        self.assertTrue(
            target_return_is_reached(
                agent=agent,
                env=env,
                target_return=-250,
                max_episodes=1000,
                learn=True,
                learn_after_episode=True,
                exploit=False,
                check_moving_average=True,
            )
        )

    def test_cql_offline_training(self) -> None:
        """
        This test is checking if DQN with conservative loss will eventually get to > 100 return for CartPole-v1
        when trained with offline data.
        """
        set_seed(100)
        env = GymEnvironment("CartPole-v1")
        conservativeDQN_agent = PearlAgent(
            policy_learner=DeepQLearning(
                state_dim=env.observation_space.shape[0],
                action_space=env.action_space,
                hidden_dims=[64, 64],
                training_rounds=100,
                is_conservative=True,
                conservative_alpha=4.0,
                batch_size=128,
            ),
            replay_buffer=FIFOOffPolicyReplayBuffer(10000),
        )

        # specify path for offline data set
        url = "https://raw.githubusercontent.com/jb3618columbia/offline_data/ee11452e5c6116d12cd3c1cab25aff39ad7d6ebf/offline_raw_transitions_dict_50k.pt"

        # train conservative agent with offline data
        offline_learning(url, offline_agent=conservativeDQN_agent, training_epochs=2000)

        # offline evaluation
        conservativeDQN_agent_returns = offline_evaluation(
            offline_agent=conservativeDQN_agent, env=env
        )

        self.assertTrue(max(conservativeDQN_agent_returns) > 50)