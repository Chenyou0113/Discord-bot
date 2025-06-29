# 優化的圖片嵌入程式碼

    def create_embed_with_optimized_image(self, index: int):
        """創建監視器 embed - 最終優化版本"""
        if not (0 <= index < self.total_cameras):
            return None
        
        data = self.cameras[index]
        info = self.cog.format_water_image_info(data)
        
        if not info:
            return None
        
        embed = discord.Embed(
            title=f"📸 {info['station_name']}",
            description=f"📍 **位置**: {info['location']}\n"
                      f"🌊 **河川**: {info['river']}\n"
                      f"📡 **狀態**: {info['status']}",
            color=discord.Color.blue()
        )
        
        # 最終優化的圖片嵌入邏輯
        image_url = info.get('image_url', '')
        image_embedded = False
        
        if image_url and image_url != 'N/A' and image_url.strip():
            try:
                # 最佳化 URL 處理
                processed_url = self._process_and_validate_image_url(image_url)
                
                if processed_url:
                    # 主要圖片嵌入
                    embed.set_image(url=processed_url)
                    image_embedded = True
                    
                    # 詳細資訊欄位
                    embed.add_field(
                        name="📸 即時監控影像",
                        value=f"🎥 **監控點**: {info['station_name']}\n"
                              f"📷 **設備**: {info.get('camera_name', '主攝影機')}\n"
                              f"🔗 [查看原圖]({processed_url})\n"
                              f"🕐 **更新**: 即時監控",
                        inline=False
                    )
                    
                    # 備用縮圖（提高顯示成功率）
                    try:
                        embed.set_thumbnail(url=processed_url)
                    except:
                        logger.debug("縮圖設定失敗，但不影響主圖顯示")
                    
                    logger.info(f"✅ 圖片嵌入成功: {info['station_name']} - {processed_url[:50]}...")
                    
            except Exception as e:
                logger.error(f"圖片嵌入處理錯誤: {str(e)}")
                image_embedded = False
        
        # 如果圖片嵌入失敗，提供替代資訊
        if not image_embedded:
            embed.add_field(
                name="⚠️ 影像狀態",
                value="目前暫無可用的即時影像\n"
                      "可能原因：監控設備維護中或網路連線問題\n"
                      "請稍後重新查詢或選擇其他監控點",
                inline=False
            )
            embed.set_thumbnail(url="https://opendata.wra.gov.tw/favicon.ico")
        
        # 設定 footer
        embed.set_footer(
            text=f"🌊 {self.location}地區水利監視器 • 經濟部水利署 • 即時監控影像",
            icon_url="https://opendata.wra.gov.tw/favicon.ico" if image_embedded else None
        )
        
        return embed

    def _process_and_validate_image_url(self, url):
        """處理和驗證圖片 URL - 最終優化版本"""
        if not url or url == 'N/A':
            return None
        
        processed_url = url.strip()
        
        # URL 格式標準化
        if not processed_url.startswith(('http://', 'https://')):
            if processed_url.startswith('//'):
                processed_url = 'https:' + processed_url
            elif processed_url.startswith('/'):
                processed_url = 'https://opendata.wra.gov.tw' + processed_url
            else:
                # 嘗試不同的基礎 URL
                possible_bases = [
                    'https://fmg.wra.gov.tw/',
                    'https://opendata.wra.gov.tw/',
                    'https://www.wra.gov.tw/'
                ]
                for base in possible_bases:
                    test_url = base + processed_url
                    if self._validate_image_url_format(test_url):
                        processed_url = test_url
                        break
        
        # 最終格式驗證
        if self._validate_image_url_format(processed_url):
            # 額外的 Discord 特殊處理
            if '&' in processed_url:
                # 確保 URL 編碼正確
                processed_url = processed_url.replace(' ', '%20')
            
            return processed_url
        
        return None

    def _validate_image_url_format(self, url):
        """驗證圖片 URL 格式 - 最終版本"""
        if not url:
            return False
        
        # 基本 URL 格式檢查
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...  
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(url):
            return False
        
        # Discord 特殊檢查
        # 確保不包含可能導致問題的字符
        problematic_chars = ['<', '>', '"', '\n', '\r', '\t']
        if any(char in url for char in problematic_chars):
            return False
        
        # 長度檢查（Discord 有 URL 長度限制）
        if len(url) > 2000:
            return False
        
        return True


# 權限檢查指令

    @app_commands.command(name="check_permissions", description="檢查機器人權限設定")
    async def check_permissions(self, interaction: discord.Interaction):
        """檢查機器人權限"""
        await interaction.response.defer()
        
        try:
            # 獲取機器人在當前頻道的權限
            permissions = interaction.channel.permissions_for(interaction.guild.me)
            
            embed = discord.Embed(
                title="🔐 機器人權限檢查",
                description="檢查圖片嵌入所需的權限狀態",
                color=discord.Color.blue()
            )
            
            # 檢查關鍵權限
            key_permissions = {
                'send_messages': ('發送訊息', permissions.send_messages),
                'embed_links': ('嵌入連結 ⭐', permissions.embed_links),
                'attach_files': ('附加檔案', permissions.attach_files),
                'use_external_emojis': ('外部表情符號', permissions.use_external_emojis),
                'read_message_history': ('讀取訊息歷史', permissions.read_message_history)
            }
            
            permission_status = []
            all_good = True
            
            for perm_key, (perm_name, has_perm) in key_permissions.items():
                status = "✅" if has_perm else "❌"
                permission_status.append(f"{status} {perm_name}")
                
                if perm_key in ['send_messages', 'embed_links'] and not has_perm:
                    all_good = False
            
            embed.add_field(
                name="權限狀態",
                value="\n".join(permission_status),
                inline=False
            )
            
            if all_good:
                embed.add_field(
                    name="✅ 狀態良好",
                    value="機器人具備圖片嵌入所需的基本權限",
                    inline=False
                )
                embed.color = discord.Color.green()
            else:
                embed.add_field(
                    name="⚠️ 權限不足",
                    value="請檢查伺服器設定，確保機器人具備 `嵌入連結` 權限",
                    inline=False
                )
                embed.color = discord.Color.red()
            
            # 測試圖片嵌入
            test_image_url = "https://fmg.wra.gov.tw/109wraweb/getImage.aspx?mode=getNewImageS&CCTV_SN=0x020000008E56B875DE0F514A20F9A0FEC0A36B9B2F796E7F9A375C48E448F68A9467719F623F50DC94F09300BFE6BAF9DF3418C0"
            
            test_embed = discord.Embed(
                title="🧪 圖片嵌入測試",
                description="如果您能看到下方的監視器圖片，表示權限設定正確",
                color=discord.Color.blue()
            )
            test_embed.set_image(url=test_image_url)
            
            await interaction.followup.send(embeds=[embed, test_embed])
            
        except Exception as e:
            error_embed = discord.Embed(
                title="❌ 權限檢查失敗",
                description=f"檢查過程中發生錯誤：{str(e)}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=error_embed)
