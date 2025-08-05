def _get_majority_tier(self, player_puuids: list, queue_type="RANKED_SOLO_5x5"):
        """
        Determines the most common ranked tier among a list of players.

        Args:
            player_puuids (list): List of player puuids (unique Riot identifiers).

        Returns:
            str: The tier (e.g., "GOLD", "DIAMOND") with the highest frequency.

        Notes:
            - Makes an API call per player.
            - Skips players with missing or unknown tier information.
        """

        tier_freq_dict = {}

        game_tier = self._get_majority_tier(
                    match_data["metadata"]['participants'], self.queue_type)
        
        for puuid in player_puuids:
            time.sleep(self.sleep_duration_after_API_call)

            try:
                tier = self.CallsAPI.get_summoner_tier_from_puuid(
                    puuid, queue_type)

            except Exception as e:
                self.logger.error(f"{e}")

            if tier:
                tier_freq_dict[tier] = tier_freq_dict.get(tier, 0) + 1

            self.logger.info(tier)
            if tier_freq_dict[tier] >= 6:
                return tier

            # self.logger.info(tier)
        return max(tier_freq_dict, key=tier_freq_dict.get)