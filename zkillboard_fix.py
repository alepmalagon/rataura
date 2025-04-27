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
    
    # Instead of using the zKillboard API, we'll scrape the zKillboard website directly
    # This is more reliable as the API has restrictions and rate limits
    
    # Construct the zKillboard URL for web scraping
    zkillboard_base_url = "https://zkillboard.com"
    
    # Build the URL path based on the parameters
    url_parts = [zkillboard_base_url]
    
    if character_id:
        url_parts.append(f"character/{character_id}")
    elif corporation_id:
        url_parts.append(f"corporation/{corporation_id}")
    elif alliance_id:
        url_parts.append(f"alliance/{alliance_id}")
    
    if ship_type_id:
        url_parts.append(f"ship/{ship_type_id}")
    
    if losses_only:
        url_parts.append("losses")
    elif kills_only:
        url_parts.append("kills")
    
    # Join the URL parts
    zkillboard_url = "/".join(url_parts) + "/"
    
    logger.info(f"Fetching killmail data from zKillboard website: {zkillboard_url}")
    
    try:
        # Make the request to zKillboard with proper headers
        headers = {
            "User-Agent": "Rataura/1.0.0 (EVE Online Livekit Agent; https://github.com/alepmalagon/rataura; maintainer: alepmalagon@github.com)",
            "Accept": "text/html,application/xhtml+xml,application/xml",
            "Accept-Encoding": "gzip, deflate, br"
        }
        
        async with aiohttp.ClientSession() as session:
            # Add a delay to avoid rate limiting
            await asyncio.sleep(2)
            
            async with session.get(zkillboard_url, headers=headers) as response:
                if response.status == 200:
                    # Get the HTML content
                    html_content = await response.text()
                    logger.info(f"Retrieved HTML content from zKillboard, size: {len(html_content)} bytes")
                    
                    # Parse the HTML to extract killmail information
                    # We'll use a simple approach to extract the killmail data from the HTML
                    
                    # Extract killmail IDs from the HTML
                    killmail_ids = re.findall(r'href="/kill/(\d+)/"', html_content)
                    unique_killmail_ids = list(dict.fromkeys(killmail_ids))  # Remove duplicates
                    
                    # Limit the number of killmails
                    killmail_ids = unique_killmail_ids[:limit]
                    
                    logger.info(f"Found {len(killmail_ids)} unique killmail IDs")
                    
                    if not killmail_ids:
                        logger.warning(f"No killmails found at {zkillboard_url}")
                        
                        # Create a formatted summary for no results
                        entity_name = character_name or corporation_name or alliance_name or "Unknown"
                        ship_name = ship_type_name or "Unknown"
                        
                        if entity_name != "Unknown" and ship_name != "Unknown":
                            if losses_only:
                                summary = f"No recent {ship_name} losses found for {entity_name}."
                            elif kills_only:
                                summary = f"No recent {ship_name} kills found for {entity_name}."
                            else:
                                summary = f"No recent {ship_name} killmails found for {entity_name}."
                        elif entity_name != "Unknown":
                            if losses_only:
                                summary = f"No recent losses found for {entity_name}."
                            elif kills_only:
                                summary = f"No recent kills found for {entity_name}."
                            else:
                                summary = f"No recent killmails found for {entity_name}."
                        elif ship_name != "Unknown":
                            if losses_only:
                                summary = f"No recent {ship_name} losses found."
                            elif kills_only:
                                summary = f"No recent {ship_name} kills found."
                            else:
                                summary = f"No recent {ship_name} killmails found."
                        else:
                            summary = "No recent killmails found."
                        
                        return {
                            "killmails": [],
                            "formatted_info": summary,
                        }
                    
                    # Extract basic information for each killmail from the HTML
                    processed_killmails = []
                    
                    # Extract killmail rows
                    killmail_rows = re.findall(r'<tr.*?data-killid="(\d+)".*?>(.*?)</tr>', html_content, re.DOTALL)
                    
                    for killmail_id, row_content in killmail_rows:
                        if killmail_id not in killmail_ids:
                            continue
                        
                        try:
                            # Extract timestamp
                            timestamp_match = re.search(r'<td.*?class="hidden-xs".*?data-order="(\d+)".*?>(.*?)</td>', row_content, re.DOTALL)
                            timestamp = "Unknown time"
                            if timestamp_match:
                                # Convert Unix timestamp to readable format
                                unix_timestamp = int(timestamp_match.group(1))
                                timestamp = datetime.datetime.fromtimestamp(unix_timestamp).strftime('%Y-%m-%d %H:%M:%S')
                            
                            # Extract ship type
                            ship_match = re.search(r'<td.*?class="hidden-xs".*?><a.*?title="([^"]+)".*?><img.*?></a></td>', row_content, re.DOTALL)
                            ship_name = "Unknown Ship"
                            if ship_match:
                                ship_name = ship_match.group(1)
                            
                            # Extract victim name
                            victim_match = re.search(r'<td.*?class="victim".*?><a.*?>(.*?)</a></td>', row_content, re.DOTALL)
                            victim_name = "Unknown"
                            if victim_match:
                                victim_name = victim_match.group(1).strip()
                            
                            # Extract final blow
                            final_blow_match = re.search(r'<td.*?class="finalBlow".*?><a.*?>(.*?)</a></td>', row_content, re.DOTALL)
                            final_blow_name = "Unknown"
                            if final_blow_match:
                                final_blow_name = final_blow_match.group(1).strip()
                            
                            # Extract system
                            system_match = re.search(r'<td.*?><a.*?title="([^"]+)".*?><span.*?>(.*?)</span></a></td>', row_content, re.DOTALL)
                            system_name = "Unknown System"
                            if system_match:
                                system_name = system_match.group(1)
                            
                            # Extract ISK value
                            value_match = re.search(r'<td.*?class="hidden-xs".*?>([\d,.]+)</td>', row_content, re.DOTALL)
                            value_str = "0"
                            if value_match:
                                value_str = value_match.group(1).replace(',', '')
                            
                            try:
                                total_value = float(value_str)
                            except ValueError:
                                total_value = 0
                            
                            # Create a processed killmail entry
                            processed_killmail = {
                                "killmail_id": killmail_id,
                                "killmail_time": timestamp,
                                "victim_name": victim_name,
                                "victim_ship_name": ship_name,
                                "final_blow_name": final_blow_name,
                                "final_blow_ship_name": "Unknown Ship",  # Not easily extractable from the HTML
                                "solar_system_name": system_name,
                                "total_value": total_value,
                                "zkillboard_url": f"https://zkillboard.com/kill/{killmail_id}/",
                            }
                            
                            processed_killmails.append(processed_killmail)
                            
                            # Stop if we've reached the limit
                            if len(processed_killmails) >= limit:
                                break
                                
                        except Exception as e:
                            logger.error(f"Error processing killmail row: {e}", exc_info=True)
                    
                    # Create a formatted summary
                    entity_name = character_name or corporation_name or alliance_name
                    if not entity_name:
                        if character_id:
                            try:
                                character_info = await esi_client.get_character(character_id)
                                entity_name = character_info.get("name", f"Character ID {character_id}")
                            except Exception:
                                entity_name = f"Character ID {character_id}"
                        elif corporation_id:
                            try:
                                corporation_info = await esi_client.get_corporation(corporation_id)
                                entity_name = corporation_info.get("name", f"Corporation ID {corporation_id}")
                            except Exception:
                                entity_name = f"Corporation ID {corporation_id}"
                        elif alliance_id:
                            try:
                                alliance_info = await esi_client.get_alliance(alliance_id)
                                entity_name = alliance_info.get("name", f"Alliance ID {alliance_id}")
                            except Exception:
                                entity_name = f"Alliance ID {alliance_id}"
                        else:
                            entity_name = "Unknown"
                    
                    if not ship_type_name and ship_type_id:
                        try:
                            ship_info = await esi_client.get_type(ship_type_id)
                            ship_type_name = ship_info.get("name", f"Ship Type ID {ship_type_id}")
                        except Exception:
                            ship_type_name = f"Ship Type ID {ship_type_id}"
                    
                    # Create a formatted summary
                    summary = ""
                    
                    if entity_name and ship_type_name:
                        if losses_only:
                            summary = f"Recent {ship_type_name} losses for {entity_name}:\n\n"
                        elif kills_only:
                            summary = f"Recent {ship_type_name} kills for {entity_name}:\n\n"
                        else:
                            summary = f"Recent {ship_type_name} killmails for {entity_name}:\n\n"
                    elif entity_name:
                        if losses_only:
                            summary = f"Recent losses for {entity_name}:\n\n"
                        elif kills_only:
                            summary = f"Recent kills for {entity_name}:\n\n"
                        else:
                            summary = f"Recent killmails for {entity_name}:\n\n"
                    elif ship_type_name:
                        if losses_only:
                            summary = f"Recent {ship_type_name} losses:\n\n"
                        elif kills_only:
                            summary = f"Recent {ship_type_name} kills:\n\n"
                        else:
                            summary = f"Recent {ship_type_name} killmails:\n\n"
                    else:
                        summary = "Recent killmails:\n\n"
                    
                    # Add each killmail to the summary
                    for i, killmail in enumerate(processed_killmails):
                        summary += f"{i+1}. "
                        
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
                        solar_system_name = killmail.get("solar_system_name", "Unknown System")
                        killmail_time = killmail.get("killmail_time", "Unknown time")
                        
                        summary += f"{victim_name} lost a {victim_ship_name} ({formatted_value}) in {solar_system_name} on {killmail_time}. "
                        summary += f"Final blow by {final_blow_name}.\n"
                        summary += f"   zKillboard: {killmail.get('zkillboard_url', 'Unknown')}\n\n"
                    
                    if not processed_killmails:
                        if entity_name and ship_type_name:
                            if losses_only:
                                summary = f"No recent {ship_type_name} losses found for {entity_name}."
                            elif kills_only:
                                summary = f"No recent {ship_type_name} kills found for {entity_name}."
                            else:
                                summary = f"No recent {ship_type_name} killmails found for {entity_name}."
                        elif entity_name:
                            if losses_only:
                                summary = f"No recent losses found for {entity_name}."
                            elif kills_only:
                                summary = f"No recent kills found for {entity_name}."
                            else:
                                summary = f"No recent killmails found for {entity_name}."
                        elif ship_type_name:
                            if losses_only:
                                summary = f"No recent {ship_type_name} losses found."
                            elif kills_only:
                                summary = f"No recent {ship_type_name} kills found."
                            else:
                                summary = f"No recent {ship_type_name} killmails found."
                        else:
                            summary = "No recent killmails found."
                    
                    return {
                        "killmails": processed_killmails,
                        "formatted_info": summary,
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"zKillboard website error: {response.status} - {error_text[:200]}")
                    
                    # Provide a more user-friendly error message for common errors
                    if response.status == 403:
                        return {
                            "error": "Access to zKillboard website is currently restricted. This could be due to rate limiting or IP restrictions.",
                            "technical_details": f"zKillboard website error: {response.status}",
                            "troubleshooting": "Try again later or check if your IP is being blocked."
                        }
                    elif response.status == 404:
                        return {
                            "error": "The requested resource was not found on zKillboard.",
                            "technical_details": f"zKillboard website error: {response.status}"
                        }
                    elif response.status == 429:
                        return {
                            "error": "You've been rate limited by zKillboard. Please wait before making more requests.",
                            "technical_details": f"zKillboard website error: {response.status}"
                        }
                    
                    return {"error": f"zKillboard website error: {response.status}"}
    except Exception as e:
        logger.error(f"Error getting killmail info: {e}", exc_info=True)
        return {"error": f"Error getting killmail info: {str(e)}"}
