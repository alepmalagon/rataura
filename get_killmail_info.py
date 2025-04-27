async def get_killmail_info(
    character_id: Optional[int] = None, 
    character_name: Optional[str] = None,
    corporation_id: Optional[int] = None, 
    corporation_name: Optional[str] = None,
    alliance_id: Optional[int] = None, 
    alliance_name: Optional[str] = None,
    ship_type_id: Optional[int] = None, 
    ship_type_name: Optional[str] = None,
    limit: int = 5,
    losses_only: bool = False,
    kills_only: bool = False
) -> Dict[str, Any]:
    """
    Get information about recent killmails for a character, corporation, alliance, or ship type from zKillboard.
    
    Args:
        character_id (Optional[int], optional): The ID of the character to get killmails for.
        character_name (Optional[str], optional): The name of the character to get killmails for.
        corporation_id (Optional[int], optional): The ID of the corporation to get killmails for.
        corporation_name (Optional[str], optional): The name of the corporation to get killmails for.
        alliance_id (Optional[int], optional): The ID of the alliance to get killmails for.
        alliance_name (Optional[str], optional): The name of the alliance to get killmails for.
        ship_type_id (Optional[int], optional): The ID of the ship type to get killmails for.
        ship_type_name (Optional[str], optional): The name of the ship type to get killmails for.
        limit (int, optional): The maximum number of killmails to return. Defaults to 5.
        losses_only (bool, optional): Whether to only return losses. Defaults to False.
        kills_only (bool, optional): Whether to only return kills. Defaults to False.
    
    Returns:
        Dict[str, Any]: Information about recent killmails.
    """
    esi_client = get_esi_client()
    
    # Resolve names to IDs if provided
    if character_name and not character_id:
        logger.info(f"Resolving character name '{character_name}' to ID")
        search_result = await esi_client.search(character_name, ["character"], strict=True)
        if "character" in search_result and search_result["character"]:
            character_id = search_result["character"][0]
            logger.info(f"Resolved character name '{character_name}' to ID {character_id}")
        else:
            logger.error(f"Character '{character_name}' not found")
            return {"error": f"Character '{character_name}' not found"}
    
    if corporation_name and not corporation_id:
        logger.info(f"Resolving corporation name '{corporation_name}' to ID")
        search_result = await esi_client.search(corporation_name, ["corporation"], strict=True)
        if "corporation" in search_result and search_result["corporation"]:
            corporation_id = search_result["corporation"][0]
            logger.info(f"Resolved corporation name '{corporation_name}' to ID {corporation_id}")
        else:
            logger.error(f"Corporation '{corporation_name}' not found")
            return {"error": f"Corporation '{corporation_name}' not found"}
    
    if alliance_name and not alliance_id:
        logger.info(f"Resolving alliance name '{alliance_name}' to ID")
        search_result = await esi_client.search(alliance_name, ["alliance"], strict=True)
        if "alliance" in search_result and search_result["alliance"]:
            alliance_id = search_result["alliance"][0]
            logger.info(f"Resolved alliance name '{alliance_name}' to ID {alliance_id}")
        else:
            logger.error(f"Alliance '{alliance_name}' not found")
            return {"error": f"Alliance '{alliance_name}' not found"}
    
    if ship_type_name and not ship_type_id:
        logger.info(f"Resolving ship type name '{ship_type_name}' to ID")
        search_result = await esi_client.search(ship_type_name, ["inventory_type"], strict=True)
        if "inventory_type" in search_result and search_result["inventory_type"]:
            ship_type_id = search_result["inventory_type"][0]
            logger.info(f"Resolved ship type name '{ship_type_name}' to ID {ship_type_id}")
        else:
            logger.error(f"Ship type '{ship_type_name}' not found")
            return {"error": f"Ship type '{ship_type_name}' not found"}
    
    # Construct the zKillboard API URL according to their documentation
    # https://github.com/zKillboard/zKillboard/wiki/API-(Killmails)
    zkillboard_base_url = "https://zkillboard.com/api"
    
    # Build the URL path with modifiers
    url_parts = [zkillboard_base_url]
    
    # Add kill/loss filter
    if losses_only:
        url_parts.append("losses")
    elif kills_only:
        url_parts.append("kills")
    
    # Add entity filters
    if character_id:
        url_parts.append(f"characterID/{character_id}")
    elif corporation_id:
        url_parts.append(f"corporationID/{corporation_id}")
    elif alliance_id:
        url_parts.append(f"allianceID/{alliance_id}")
    
    # Add ship type filter
    if ship_type_id:
        url_parts.append(f"shipTypeID/{ship_type_id}")
    
    # Add page limit
    if limit and limit > 0:
        # Ensure limit doesn't exceed 200 (zkillboard max)
        actual_limit = min(limit, 200)
        url_parts.append(f"page/1")  # Always start with page 1
    
    # Ensure URL ends with a forward slash
    api_url = "/".join(url_parts) + "/"
    
    logger.info(f"Fetching killmail data from zKillboard: {api_url}")
    
    try:
        # Make the request to zKillboard with proper headers as required by their documentation
        headers = {
            "User-Agent": "Rataura/1.0.0 (EVE Online Livekit Agent; https://github.com/alepmalagon/rataura; maintainer: alepmalagon@github.com)",
            "Accept": "application/json",
            "Accept-Encoding": "gzip"
        }
        
        async with aiohttp.ClientSession() as session:
            # Add a delay to avoid rate limiting
            await asyncio.sleep(2)
            
            async with session.get(api_url, headers=headers) as response:
                if response.status == 200:
                    try:
                        # Try to parse the response as JSON
                        content_type = response.headers.get('Content-Type', '')
                        logger.info(f"Response content type: {content_type}")
                        
                        # Get the raw content for debugging
                        content = await response.read()
                        logger.info(f"Response size: {len(content)} bytes")
                        
                        # If it's HTML, we need to handle it differently
                        if 'text/html' in content_type:
                            logger.error(f"Received HTML instead of JSON. This might be a rate limit or blocking issue.")
                            return {
                                "error": "zKillboard returned HTML instead of JSON. This is likely due to rate limiting or IP restrictions.",
                                "technical_details": "Try again later or check if your IP is being blocked."
                            }
                        
                        # Try to decode the JSON
                        try:
                            killmails = await response.json()
                            logger.info(f"Retrieved {len(killmails)} killmails from zKillboard")
                        except Exception as e:
                            logger.error(f"Error parsing zKillboard response: {e}")
                            # Try to get the content as text for debugging
                            text_content = content.decode('utf-8', errors='replace')
                            logger.error(f"Response content: {text_content[:200]}...")  # Log first 200 chars
                            return {"error": f"Error parsing zKillboard response: {str(e)}"}
                        
                        # Process the killmails
                        processed_killmails = []
                        for killmail in killmails:
                            try:
                                # Get basic killmail info from the zkillboard response
                                killmail_id = killmail.get("killmail_id")
                                if not killmail_id:
                                    # zkillboard API returns different format than expected
                                    # Try to extract from zkb data
                                    zkb = killmail.get("zkb", {})
                                    killmail_id = zkb.get("killID")
                                
                                # Get timestamp
                                killmail_time = killmail.get("killmail_time")
                                if not killmail_time:
                                    # Try alternative field
                                    killmail_time = killmail.get("killTime")
                                
                                # Get victim info - structure depends on API response format
                                victim = killmail.get("victim", {})
                                victim_id = victim.get("character_id") or victim.get("characterID")
                                victim_name = "Unknown"
                                victim_ship_type_id = victim.get("ship_type_id") or victim.get("shipTypeID")
                                victim_ship_name = "Unknown Ship"
                                
                                # Get attacker info
                                attackers = killmail.get("attackers", [])
                                final_blow_attacker = next((a for a in attackers if a.get("final_blow") == 1), None)
                                final_blow_id = None
                                final_blow_name = "Unknown"
                                final_blow_ship_type_id = None
                                final_blow_ship_name = "Unknown Ship"
                                
                                if final_blow_attacker:
                                    final_blow_id = final_blow_attacker.get("character_id") or final_blow_attacker.get("characterID")
                                    final_blow_ship_type_id = final_blow_attacker.get("ship_type_id") or final_blow_attacker.get("shipTypeID")
                                
                                # Get solar system info
                                solar_system_id = killmail.get("solar_system_id") or killmail.get("solarSystemID")
                                solar_system_name = "Unknown System"
                                
                                # Get zkillboard URL and value
                                zkb = killmail.get("zkb", {})
                                total_value = zkb.get("totalValue", 0)
                                
                                # Resolve IDs to names using ESI API
                                tasks = []
                                
                                # Resolve victim character name
                                if victim_id:
                                    tasks.append(esi_client.get_character(victim_id))
                                
                                # Resolve victim ship name
                                if victim_ship_type_id:
                                    tasks.append(esi_client.get_type(victim_ship_type_id))
                                
                                # Resolve final blow character name
                                if final_blow_id:
                                    tasks.append(esi_client.get_character(final_blow_id))
                                
                                # Resolve final blow ship name
                                if final_blow_ship_type_id:
                                    tasks.append(esi_client.get_type(final_blow_ship_type_id))
                                
                                # Resolve solar system name
                                if solar_system_id:
                                    tasks.append(esi_client.get_system(solar_system_id))
                                
                                # Wait for all tasks to complete
                                results = await asyncio.gather(*tasks, return_exceptions=True)
                                
                                # Process results
                                result_index = 0
                                
                                # Process victim character name
                                if victim_id:
                                    if isinstance(results[result_index], dict):
                                        victim_name = results[result_index].get("name", "Unknown")
                                    result_index += 1
                                
                                # Process victim ship name
                                if victim_ship_type_id:
                                    if isinstance(results[result_index], dict):
                                        victim_ship_name = results[result_index].get("name", "Unknown Ship")
                                    result_index += 1
                                
                                # Process final blow character name
                                if final_blow_id:
                                    if isinstance(results[result_index], dict):
                                        final_blow_name = results[result_index].get("name", "Unknown")
                                    result_index += 1
                                
                                # Process final blow ship name
                                if final_blow_ship_type_id:
                                    if isinstance(results[result_index], dict):
                                        final_blow_ship_name = results[result_index].get("name", "Unknown Ship")
                                    result_index += 1
                                
                                # Process solar system name
                                if solar_system_id:
                                    if isinstance(results[result_index], dict):
                                        solar_system_name = results[result_index].get("name", "Unknown System")
                                    result_index += 1
                                
                                # Create a processed killmail entry
                                processed_killmail = {
                                    "killmail_id": killmail_id,
                                    "killmail_time": killmail_time,
                                    "victim_id": victim_id,
                                    "victim_name": victim_name,
                                    "victim_ship_type_id": victim_ship_type_id,
                                    "victim_ship_name": victim_ship_name,
                                    "final_blow_id": final_blow_id,
                                    "final_blow_name": final_blow_name,
                                    "final_blow_ship_type_id": final_blow_ship_type_id,
                                    "final_blow_ship_name": final_blow_ship_name,
                                    "solar_system_id": solar_system_id,
                                    "solar_system_name": solar_system_name,
                                    "total_value": total_value,
                                    "zkillboard_url": f"https://zkillboard.com/kill/{killmail_id}/",
                                }
                                
                                processed_killmails.append(processed_killmail)
                            except Exception as e:
                                logger.error(f"Error processing killmail: {e}", exc_info=True)
                        
                        # Create a formatted summary
                        entity_name = None
                        entity_type = None
                        
                        if character_id:
                            entity_type = "character"
                            if character_name:
                                entity_name = character_name
                            else:
                                try:
                                    character_info = await esi_client.get_character(character_id)
                                    entity_name = character_info.get("name", f"Character ID {character_id}")
                                except Exception:
                                    entity_name = f"Character ID {character_id}"
                        elif corporation_id:
                            entity_type = "corporation"
                            if corporation_name:
                                entity_name = corporation_name
                            else:
                                try:
                                    corporation_info = await esi_client.get_corporation(corporation_id)
                                    entity_name = corporation_info.get("name", f"Corporation ID {corporation_id}")
                                except Exception:
                                    entity_name = f"Corporation ID {corporation_id}"
                        elif alliance_id:
                            entity_type = "alliance"
                            if alliance_name:
                                entity_name = alliance_name
                            else:
                                try:
                                    alliance_info = await esi_client.get_alliance(alliance_id)
                                    entity_name = alliance_info.get("name", f"Alliance ID {alliance_id}")
                                except Exception:
                                    entity_name = f"Alliance ID {alliance_id}"
                        
                        ship_name = None
                        if ship_type_id:
                            if ship_type_name:
                                ship_name = ship_type_name
                            else:
                                try:
                                    ship_info = await esi_client.get_type(ship_type_id)
                                    ship_name = ship_info.get("name", f"Ship Type ID {ship_type_id}")
                                except Exception:
                                    ship_name = f"Ship Type ID {ship_type_id}"
                        
                        # Create a formatted summary
                        summary = ""
                        
                        if entity_name and ship_name:
                            if losses_only:
                                summary = f"Recent {ship_name} losses for {entity_name}:\n\n"
                            elif kills_only:
                                summary = f"Recent {ship_name} kills for {entity_name}:\n\n"
                            else:
                                summary = f"Recent {ship_name} killmails for {entity_name}:\n\n"
                        elif entity_name:
                            if losses_only:
                                summary = f"Recent losses for {entity_name}:\n\n"
                            elif kills_only:
                                summary = f"Recent kills for {entity_name}:\n\n"
                            else:
                                summary = f"Recent killmails for {entity_name}:\n\n"
                        elif ship_name:
                            if losses_only:
                                summary = f"Recent {ship_name} losses:\n\n"
                            elif kills_only:
                                summary = f"Recent {ship_name} kills:\n\n"
                            else:
                                summary = f"Recent {ship_name} killmails:\n\n"
                        else:
                            summary = "Recent killmails:\n\n"
                        
                        # Add each killmail to the summary
                        for i, killmail in enumerate(processed_killmails):
                            summary += f"{i+1}. "
                            
                            # Format the killmail time
                            killmail_time = killmail.get("killmail_time", "Unknown time")
                            if killmail_time and killmail_time != "Unknown time":
                                try:
                                    # Convert to a more readable format
                                    killmail_time = killmail_time.replace("T", " ").replace("Z", "")
                                except Exception:
                                    pass
                            
                            # Format the ISK value
                            total_value = killmail.get("total_value", 0)
                            if total_value:
                                if total_value >= 1000000000:  # Billions
                                    formatted_value = f"{total_value / 1000000000:.2f}B ISK"
                                elif total_value >= 1000000:  # Millions
                                    formatted_value = f"{total_value / 1000000:.2f}M ISK"
                                elif total_value >= 1000:  # Thousands
                                    formatted_value = f"{total_value / 1000:.2f}K ISK"
                                else:
                                    formatted_value = f"{total_value:.2f} ISK"
                            else:
                                formatted_value = "Unknown value"
                            
                            # Add the killmail details
                            victim_name = killmail.get("victim_name", "Unknown")
                            victim_ship_name = killmail.get("victim_ship_name", "Unknown Ship")
                            final_blow_name = killmail.get("final_blow_name", "Unknown")
                            final_blow_ship_name = killmail.get("final_blow_ship_name", "Unknown Ship")
                            solar_system_name = killmail.get("solar_system_name", "Unknown System")
                            
                            summary += f"{victim_name} lost a {victim_ship_name} ({formatted_value}) in {solar_system_name} on {killmail_time}. "
                            summary += f"Final blow by {final_blow_name} in a {final_blow_ship_name}.\n"
                            summary += f"   zKillboard: {killmail.get('zkillboard_url', 'Unknown')}\n\n"
                        
                        if not processed_killmails:
                            if entity_name and ship_name:
                                if losses_only:
                                    summary = f"No recent {ship_name} losses found for {entity_name}."
                                elif kills_only:
                                    summary = f"No recent {ship_name} kills found for {entity_name}."
                                else:
                                    summary = f"No recent {ship_name} killmails found for {entity_name}."
                            elif entity_name:
                                if losses_only:
                                    summary = f"No recent losses found for {entity_name}."
                                elif kills_only:
                                    summary = f"No recent kills found for {entity_name}."
                                else:
                                    summary = f"No recent killmails found for {entity_name}."
                            elif ship_name:
                                if losses_only:
                                    summary = f"No recent {ship_name} losses found."
                                elif kills_only:
                                    summary = f"No recent {ship_name} kills found."
                                else:
                                    summary = f"No recent {ship_name} killmails found."
                            else:
                                summary = "No recent killmails found."
                        
                        return {
                            "killmails": processed_killmails,
                            "formatted_info": summary,
                        }
                    except Exception as e:
                        logger.error(f"Error processing zKillboard response: {e}", exc_info=True)
                        return {"error": f"Error processing zKillboard response: {str(e)}"}
                else:
                    error_text = await response.text()
                    logger.error(f"zKillboard API error: {response.status} - {error_text}")
                    
                    # Provide a more user-friendly error message for common errors
                    if response.status == 403:
                        return {
                            "error": "Access to zKillboard API is currently restricted. This could be due to rate limiting or IP restrictions.",
                            "technical_details": f"zKillboard API error: {response.status} - {error_text}",
                            "troubleshooting": "Try again later or check if your IP is being blocked. Make sure you're following zKillboard's API usage guidelines."
                        }
                    elif response.status == 404:
                        return {
                            "error": "The requested resource was not found on zKillboard.",
                            "technical_details": f"zKillboard API error: {response.status} - {error_text}"
                        }
                    elif response.status == 429:
                        return {
                            "error": "You've been rate limited by zKillboard. Please wait before making more requests.",
                            "technical_details": f"zKillboard API error: {response.status} - {error_text}"
                        }
                    
                    return {"error": f"zKillboard API error: {response.status} - {error_text}"}
    except Exception as e:
        logger.error(f"Error getting killmail info: {e}", exc_info=True)
        return {"error": f"Error getting killmail info: {str(e)}"}
