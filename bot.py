import discord
from discord import app_commands
from discord.ext import commands
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from typing import Optional

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

# ==================== DATABASE ====================
ROUTES = {
    "OLBA_DNMM": {"flight": "ME571", "origin": "Beirut", "dest": "Lagos", "flight_time": "6:15", "aircraft": ["A330-200"]},
    "DNMM_OLBA": {"flight": "ME572", "origin": "Lagos", "dest": "Beirut", "flight_time": "6:30", "aircraft": ["A330-200"]},
    "DNMM_DIAP": {"flight": "ME571", "origin": "Lagos", "dest": "Abidjan", "flight_time": "1:30", "aircraft": ["A330-200"]},
    "DIAP_DNMM": {"flight": "ME572", "origin": "Abidjan", "dest": "Lagos", "flight_time": "2:00", "aircraft": ["A330-200"]},
    "OLBA_DGAA": {"flight": "ME575", "origin": "Beirut", "dest": "Accra", "flight_time": "7:00", "aircraft": ["A330-200"]},
    "DGAA_OLBA": {"flight": "ME576", "origin": "Accra", "dest": "Beirut", "flight_time": "7:15", "aircraft": ["A330-200"]},
    "OLBA_HECA": {"flight": "ME304", "origin": "Beirut", "dest": "Cairo", "flight_time": "1:15", "aircraft": ["A321-200", "A320-200"]},
    "HECA_OLBA": {"flight": "ME305", "origin": "Cairo", "dest": "Beirut", "flight_time": "1:20", "aircraft": ["A321-200", "A320-200"]},
    "OLBA_LFMN": {"flight": "ME219", "origin": "Beirut", "dest": "Nice", "flight_time": "3:45", "aircraft": ["A321-200", "A320-200"]},
    "LFMN_OLBA": {"flight": "ME220", "origin": "Nice", "dest": "Beirut", "flight_time": "3:30", "aircraft": ["A321-200", "A320-200"]},
    "OLBA_LGRP": {"flight": "ME257", "origin": "Beirut", "dest": "Rhodes", "flight_time": "1:50", "aircraft": ["A320-200"]},
    "LGRP_OLBA": {"flight": "ME258", "origin": "Rhodes", "dest": "Beirut", "flight_time": "2:00", "aircraft": ["A320-200"]},
    "OLBA_EKCH": {"flight": "ME225", "origin": "Beirut", "dest": "Copenhagen", "flight_time": "4:00", "aircraft": ["A321-200", "A320-200"]},
    "EKCH_OLBA": {"flight": "ME226", "origin": "Copenhagen", "dest": "Beirut", "flight_time": "3:35", "aircraft": ["A321-200", "A320-200"]},
    "OLBA_HESH": {"flight": "ME312", "origin": "Beirut", "dest": "Sharm el Sheikh", "flight_time": "1:30", "aircraft": ["A320-200"]},
    "HESH_OLBA": {"flight": "ME313", "origin": "Sharm el Sheikh", "dest": "Beirut", "flight_time": "1:40", "aircraft": ["A320-200"]},
    "OLBA_LTAI": {"flight": "ME269", "origin": "Beirut", "dest": "Antalya", "flight_time": "1:30", "aircraft": ["A321-200", "A320-200"]},
    "LTAI_OLBA": {"flight": "ME270", "origin": "Antalya", "dest": "Beirut", "flight_time": "1:40", "aircraft": ["A321-200", "A320-200"]},
    "OLBA_LGMK": {"flight": "ME255", "origin": "Beirut", "dest": "Mykonos", "flight_time": "2:00", "aircraft": ["A320-200"]},
    "LGMK_OLBA": {"flight": "ME256", "origin": "Mykonos", "dest": "Beirut", "flight_time": "2:10", "aircraft": ["A320-200"]},
    "OLBA_OMDB": {"flight": "ME426", "origin": "Beirut", "dest": "Dubai", "flight_time": "3:10", "aircraft": ["A321-200", "A330-200"]},
    "OMDB_OLBA": {"flight": "ME427", "origin": "Dubai", "dest": "Beirut", "flight_time": "3:30", "aircraft": ["A321-200", "A330-200"]},
    "OLBA_OTHH": {"flight": "ME431", "origin": "Beirut", "dest": "Doha", "flight_time": "2:50", "aircraft": ["A321-200"]},
    "OTHH_OLBA": {"flight": "ME432", "origin": "Doha", "dest": "Beirut", "flight_time": "3:00", "aircraft": ["A321-200"]},
    "OLBA_OEJN": {"flight": "ME374", "origin": "Beirut", "dest": "Jeddah", "flight_time": "2:30", "aircraft": ["A321-200", "A320-200"]},
    "OEJN_OLBA": {"flight": "ME375", "origin": "Jeddah", "dest": "Beirut", "flight_time": "2:40", "aircraft": ["A321-200", "A320-200"]},
    "OLBA_OERK": {"flight": "ME422", "origin": "Beirut", "dest": "Riyadh", "flight_time": "2:20", "aircraft": ["A321-200", "A330-200"]},
    "OERK_OLBA": {"flight": "ME423", "origin": "Riyadh", "dest": "Beirut", "flight_time": "2:30", "aircraft": ["A321-200", "A330-200"]},
    "OLBA_OMAA": {"flight": "ME418", "origin": "Beirut", "dest": "Abu Dhabi", "flight_time": "3:10", "aircraft": ["A321-200"]},
    "OMAA_OLBA": {"flight": "ME419", "origin": "Abu Dhabi", "dest": "Beirut", "flight_time": "3:20", "aircraft": ["A321-200"]},
    "OLBA_OKKK": {"flight": "ME404", "origin": "Beirut", "dest": "Kuwait", "flight_time": "2:20", "aircraft": ["A321-200", "A320-200"]},
    "OKKK_OLBA": {"flight": "ME405", "origin": "Kuwait", "dest": "Beirut", "flight_time": "2:30", "aircraft": ["A321-200", "A320-200"]},
    "OLBA_OJAI": {"flight": "ME310", "origin": "Beirut", "dest": "Amman", "flight_time": "1:10", "aircraft": ["A321-200", "A320-200"]},
    "OJAI_OLBA": {"flight": "ME311", "origin": "Amman", "dest": "Beirut", "flight_time": "1:15", "aircraft": ["A321-200", "A320-200"]},
    "OLBA_ORBI": {"flight": "ME320", "origin": "Beirut", "dest": "Baghdad", "flight_time": "1:45", "aircraft": ["A321-200", "A320-200"]},
    "ORBI_OLBA": {"flight": "ME321", "origin": "Baghdad", "dest": "Beirut", "flight_time": "2:00", "aircraft": ["A321-200", "A320-200"]},
    "OLBA_ORER": {"flight": "ME324", "origin": "Beirut", "dest": "Erbil", "flight_time": "1:50", "aircraft": ["A321-200", "A320-200"]},
    "ORER_OLBA": {"flight": "ME325", "origin": "Erbil", "dest": "Beirut", "flight_time": "2:05", "aircraft": ["A321-200", "A320-200"]},
    "OLBA_ORNI": {"flight": "ME326", "origin": "Beirut", "dest": "Najaf", "flight_time": "1:50", "aircraft": ["A321-200", "A320-200"]},
    "ORNI_OLBA": {"flight": "ME327", "origin": "Najaf", "dest": "Beirut", "flight_time": "2:05", "aircraft": ["A321-200", "A320-200"]},
    "OLBA_UDYZ": {"flight": "ME275", "origin": "Beirut", "dest": "Yerevan", "flight_time": "2:12", "aircraft": ["A321-200", "A320-200"]},
    "UDYZ_OLBA": {"flight": "ME276", "origin": "Yerevan", "dest": "Beirut", "flight_time": "2:25", "aircraft": ["A321-200", "A320-200"]},
    "OLBA_LFPG": {"flight": "ME211", "origin": "Beirut", "dest": "Paris", "flight_time": "4:30", "aircraft": ["A330-200"]},
    "LFPG_OLBA": {"flight": "ME212", "origin": "Paris", "dest": "Beirut", "flight_time": "4:15", "aircraft": ["A330-200"]},
    "OLBA_EGLL": {"flight": "ME201", "origin": "Beirut", "dest": "London Heathrow", "flight_time": "5:05", "aircraft": ["A321-200", "A330-200"]},
    "EGLL_OLBA": {"flight": "ME202", "origin": "London Heathrow", "dest": "Beirut", "flight_time": "4:35", "aircraft": ["A321-200", "A330-200"]},
    "OLBA_EDDF": {"flight": "ME217", "origin": "Beirut", "dest": "Frankfurt", "flight_time": "4:25", "aircraft": ["A321-200", "A330-200"]},
    "EDDF_OLBA": {"flight": "ME218", "origin": "Frankfurt", "dest": "Beirut", "flight_time": "4:50", "aircraft": ["A321-200", "A330-200"]},
    "OLBA_LSGG": {"flight": "ME213", "origin": "Beirut", "dest": "Geneva", "flight_time": "4:15", "aircraft": ["A321-200", "A320-200"]},
    "LSGG_OLBA": {"flight": "ME214", "origin": "Geneva", "dest": "Beirut", "flight_time": "4:00", "aircraft": ["A321-200", "A320-200"]},
    "OLBA_LIRF": {"flight": "ME231", "origin": "Beirut", "dest": "Rome", "flight_time": "3:35", "aircraft": ["A321-200", "A330-200"]},
    "LIRF_OLBA": {"flight": "ME232", "origin": "Rome", "dest": "Beirut", "flight_time": "3:25", "aircraft": ["A321-200", "A330-200"]},
    "OLBA_LIMC": {"flight": "ME235", "origin": "Beirut", "dest": "Milan", "flight_time": "3:55", "aircraft": ["A321-200", "A320-200"]},
    "LIMC_OLBA": {"flight": "ME236", "origin": "Milan", "dest": "Beirut", "flight_time": "3:35", "aircraft": ["A321-200", "A320-200"]},
    "OLBA_LEMD": {"flight": "ME241", "origin": "Beirut", "dest": "Madrid", "flight_time": "4:30", "aircraft": ["A321-200"]},
    "LEMD_OLBA": {"flight": "ME242", "origin": "Madrid", "dest": "Beirut", "flight_time": "4:15", "aircraft": ["A321-200"]},
    "OLBA_LEBL": {"flight": "ME243", "origin": "Beirut", "dest": "Barcelona", "flight_time": "4:30", "aircraft": ["A321-200", "A320-200"]},
    "LEBL_OLBA": {"flight": "ME244", "origin": "Barcelona", "dest": "Beirut", "flight_time": "3:50", "aircraft": ["A321-200", "A320-200"]},
    "OLBA_LGAV": {"flight": "ME251", "origin": "Beirut", "dest": "Athens", "flight_time": "1:55", "aircraft": ["A321-200", "A320-200"]},
    "LGAV_OLBA": {"flight": "ME252", "origin": "Athens", "dest": "Beirut", "flight_time": "1:45", "aircraft": ["A321-200", "A320-200"]},
    "OLBA_LCLK": {"flight": "ME261", "origin": "Beirut", "dest": "Larnaca", "flight_time": "0:45", "aircraft": ["A320-200"]},
    "LCLK_OLBA": {"flight": "ME262", "origin": "Larnaca", "dest": "Beirut", "flight_time": "0:40", "aircraft": ["A320-200"]},
    "OLBA_LTFM": {"flight": "ME265", "origin": "Beirut", "dest": "Istanbul", "flight_time": "1:36", "aircraft": ["A321-200"]},
    "LTFM_OLBA": {"flight": "ME266", "origin": "Istanbul", "dest": "Beirut", "flight_time": "1:55", "aircraft": ["A321-200"]},
    "OLBA_EDDL": {"flight": "ME247", "origin": "Beirut", "dest": "Dusseldorf", "flight_time": "4:15", "aircraft": ["A321-200", "A320-200"]},
    "EDDL_OLBA": {"flight": "ME248", "origin": "Dusseldorf", "dest": "Beirut", "flight_time": "4:05", "aircraft": ["A321-200", "A320-200"]},
    "OLBA_EBBR": {"flight": "ME215", "origin": "Beirut", "dest": "Brussels", "flight_time": "4:30", "aircraft": ["A321-200", "A320-200"]},
    "EBBR_OLBA": {"flight": "ME216", "origin": "Brussels", "dest": "Beirut", "flight_time": "4:10", "aircraft": ["A321-200", "A320-200"]},
}

AIRPORT_INFO = {
    "OLBA": {"name": "Beirut-Rafic Hariri", "city": "Beirut"},
    "DNMM": {"name": "Murtala Muhammed", "city": "Lagos"},
    "DIAP": {"name": "Felix Houphouet Boigny", "city": "Abidjan"},
    "DGAA": {"name": "Kotoka", "city": "Accra"},
    "HECA": {"name": "Cairo International", "city": "Cairo"},
    "LFMN": {"name": "Nice Cote d'Azur", "city": "Nice"},
    "LGRP": {"name": "Rhodes Diagoras", "city": "Rhodes"},
    "EKCH": {"name": "Copenhagen Kastrup", "city": "Copenhagen"},
    "HESH": {"name": "Sharm el Sheikh", "city": "Sharm el Sheikh"},
    "LTAI": {"name": "Antalya", "city": "Antalya"},
    "LGMK": {"name": "Mykonos", "city": "Mykonos"},
    "OMDB": {"name": "Dubai International", "city": "Dubai"},
    "OTHH": {"name": "Hamad International", "city": "Doha"},
    "OEJN": {"name": "King Abdulaziz", "city": "Jeddah"},
    "OERK": {"name": "King Khalid", "city": "Riyadh"},
    "OMAA": {"name": "Abu Dhabi International", "city": "Abu Dhabi"},
    "OKKK": {"name": "Kuwait International", "city": "Kuwait"},
    "OJAI": {"name": "Queen Alia", "city": "Amman"},
    "ORBI": {"name": "Baghdad International", "city": "Baghdad"},
    "ORER": {"name": "Erbil International", "city": "Erbil"},
    "ORNI": {"name": "Al Najaf", "city": "Najaf"},
    "UDYZ": {"name": "Zvartnots", "city": "Yerevan"},
    "LFPG": {"name": "Charles de Gaulle", "city": "Paris"},
    "EGLL": {"name": "Heathrow", "city": "London"},
    "EDDF": {"name": "Frankfurt", "city": "Frankfurt"},
    "LSGG": {"name": "Geneva", "city": "Geneva"},
    "LIRF": {"name": "Leonardo da Vinci", "city": "Rome"},
    "LIMC": {"name": "Malpensa", "city": "Milan"},
    "LEMD": {"name": "Adolfo Suarez", "city": "Madrid"},
    "LEBL": {"name": "Barcelona-El Prat", "city": "Barcelona"},
    "LGAV": {"name": "Eleftherios Venizelos", "city": "Athens"},
    "LCLK": {"name": "Larnaca", "city": "Larnaca"},
    "LTFM": {"name": "Istanbul", "city": "Istanbul"},
    "EDDL": {"name": "Dusseldorf", "city": "Dusseldorf"},
    "EBBR": {"name": "Brussels", "city": "Brussels"},
}

AIRPORT_CODES = list(AIRPORT_INFO.keys())

# Build destination map
DESTINATIONS = {}
for route_key, route_data in ROUTES.items():
    dep_code = route_key.split("_")[0]
    arr_code = route_key.split("_")[1]
    if dep_code not in DESTINATIONS:
        DESTINATIONS[dep_code] = []
    if arr_code not in DESTINATIONS[dep_code]:
        DESTINATIONS[dep_code].append(arr_code)

# ==================== AUTO-COMPLETE FUNCTIONS ====================

def get_airport_choices(current: str) -> list:
    """Return airports matching the current input (ICAO or city name)"""
    current_lower = current.lower()
    matches = []
    for code, info in AIRPORT_INFO.items():
        if current_lower in code.lower() or current_lower in info['city'].lower():
            matches.append(app_commands.Choice(name=f"{code} - {info['city']}", value=code))
    return matches[:25]  # Discord limits to 25 choices

async def departure_autocomplete(interaction: discord.Interaction, current: str) -> list:
    return get_airport_choices(current)

async def arrival_autocomplete(interaction: discord.Interaction, current: str) -> list:
    # Get the departure from the command's namespace
    departure = interaction.namespace.departure
    if not departure:
        return []
    
    current_lower = current.lower()
    matches = []
    
    # Only show destinations available from this departure
    if departure in DESTINATIONS:
        for code in DESTINATIONS[departure]:
            info = AIRPORT_INFO.get(code)
            if info:
                if current_lower in code.lower() or current_lower in info['city'].lower():
                    matches.append(app_commands.Choice(name=f"{code} - {info['city']}", value=code))
    
    return matches[:25]

# ==================== BUTTON VIEWS ====================

class DisabledView(discord.ui.View):
    """View with disabled buttons (used after flight is landed)"""
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(label="Join Flight", style=discord.ButtonStyle.primary, disabled=True))
        self.add_item(discord.ui.Button(label="Update Status", style=discord.ButtonStyle.secondary, disabled=True))
        self.add_item(discord.ui.Button(label="Assign Gates", style=discord.ButtonStyle.success, disabled=True))

class DispatchView(discord.ui.View):
    def __init__(self, flight_data, author_id):
        super().__init__(timeout=None)
        self.flight_data = flight_data
        self.author_id = author_id
        self.thread_id = None
        self.pilots = [f"<@{author_id}>"]
        self.is_landed = False
        
    @discord.ui.button(label="Join Flight", style=discord.ButtonStyle.primary)
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.is_landed:
            await interaction.response.send_message("❌ This flight has already landed. Cannot join.", ephemeral=True)
            return
        if interaction.user.id == self.author_id:
            await interaction.response.send_message("You are the flight captain! You can't join your own flight.", ephemeral=True)
            return
        
        user_id_str = f"<@{interaction.user.id}>"
        if user_id_str not in self.pilots:
            self.pilots.append(user_id_str)
            await interaction.response.send_message(f"{user_id_str} has joined the flight!", ephemeral=False)
            
            if not self.thread_id:
                thread = await interaction.channel.create_thread(name=f"✈️ Flight {self.flight_data['flight']} Discussion", type=discord.ChannelType.public_thread)
                self.thread_id = thread.id
                await thread.send(f"**✈️ Flight {self.flight_data['flight']} Discussion**\nCaptain: <@{self.author_id}>\nPilots: {', '.join(self.pilots)}")
        else:
            await interaction.response.send_message("You already joined this flight!", ephemeral=True)
    
    @discord.ui.button(label="Update Status", style=discord.ButtonStyle.secondary)
    async def status_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.is_landed:
            await interaction.response.send_message("❌ This flight has already landed. Cannot update status.", ephemeral=True)
            return
        if interaction.user.id != self.author_id and f"<@{interaction.user.id}>" not in self.pilots:
            await interaction.response.send_message("Only pilots who joined this flight can update status.", ephemeral=True)
            return
        
        view = StatusSelectView(self.flight_data, self.author_id, self.thread_id, self.pilots, self)
        await interaction.response.send_message("Select flight status:", view=view, ephemeral=True)
    
    @discord.ui.button(label="Assign Gates", style=discord.ButtonStyle.success)
    async def gates_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.is_landed:
            await interaction.response.send_message("❌ This flight has already landed. Cannot assign gates.", ephemeral=True)
            return
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("Only the flight captain can assign gates.", ephemeral=True)
            return
        
        modal = GateAssignmentModal(self.pilots)
        await interaction.response.send_modal(modal)

class ConfirmLandedView(discord.ui.View):
    def __init__(self, flight_data, author_id, thread_id, pilots, parent_view):
        super().__init__(timeout=60)
        self.flight_data = flight_data
        self.author_id = author_id
        self.thread_id = thread_id
        self.pilots = pilots
        self.parent_view = parent_view
    
    @discord.ui.button(label="Yes, Confirm Landed", style=discord.ButtonStyle.danger)
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.parent_view.is_landed = True
        self.flight_data['status'] = "Landed"
        
        embed = discord.Embed(title=f"✈️ {self.flight_data['flight']} | MEAV", color=discord.Color.red())
        embed.description = f"**{self.flight_data['departure']}** ({self.flight_data['dep_city']}) → **{self.flight_data['arrival']}** ({self.flight_data['arr_city']})"
        embed.add_field(name="\u200b", value=f"**✈️ Aircraft:** {self.flight_data['aircraft']}", inline=False)
        embed.add_field(name="\u200b", value=f"**🕐 Flight Time:** {self.flight_data['flight_time']}", inline=False)
        embed.add_field(name="\u200b", value=f"**🛫 Departure:** {self.flight_data['dep_time']}", inline=False)
        embed.add_field(name="\u200b", value=f"**📊 Status:** Landed", inline=False)
        embed.add_field(name="\u200b", value=f"**👨‍✈️ Pilots:** {', '.join(self.pilots)}", inline=False)
        embed.add_field(name="\u200b", value=f"**📝 Notes:** {self.flight_data.get('notes', 'No notes')}", inline=False)
        embed.set_footer(text=f"Dispatched by: <@{self.author_id}> | Flight Completed")
        
        await interaction.message.edit(embed=embed, view=DisabledView())
        
        if self.thread_id:
            thread = interaction.guild.get_thread(self.thread_id)
            if thread:
                await thread.send(f"**📢 Flight Completed**\n✈️ Flight {self.flight_data['flight']} has landed. This flight is now closed.")
        
        await interaction.response.send_message("✅ Flight status updated to Landed. Buttons have been disabled.", ephemeral=True)
        self.stop()
    
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Status update cancelled.", ephemeral=True)
        self.stop()

class StatusSelectView(discord.ui.View):
    def __init__(self, flight_data, author_id, thread_id, pilots, parent_view):
        super().__init__(timeout=60)
        self.flight_data = flight_data
        self.author_id = author_id
        self.thread_id = thread_id
        self.pilots = pilots
        self.parent_view = parent_view
    
    @discord.ui.select(placeholder="Choose flight status...", options=[
        discord.SelectOption(label="Pre-flight Check", description="Before departure", emoji="✅"),
        discord.SelectOption(label="Taxi", description="Taxi to runway", emoji="🛫"),
        discord.SelectOption(label="Takeoff", description="Taking off", emoji="✈️"),
        discord.SelectOption(label="Climb", description="Climbing to altitude", emoji="⬆️"),
        discord.SelectOption(label="Cruise", description="Cruising at altitude", emoji="🌊"),
        discord.SelectOption(label="Descent", description="Descending for landing", emoji="⬇️"),
        discord.SelectOption(label="Landed", description="Landed at destination", emoji="🛬"),
        discord.SelectOption(label="Cancelled", description="Flight cancelled", emoji="❌"),
    ])
    async def status_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        status = select.values[0]
        
        if status == "Landed":
            confirm_view = ConfirmLandedView(self.flight_data, self.author_id, self.thread_id, self.pilots, self.parent_view)
            await interaction.response.send_message("⚠️ **Confirm Status Change**\nAre you sure you want to change the status to **Landed**?\n\nAfter confirming, all buttons will be disabled and the flight will be closed.", view=confirm_view, ephemeral=True)
            return
        
        self.flight_data['status'] = status
        
        embed = discord.Embed(title=f"✈️ {self.flight_data['flight']} | MEAV", color=discord.Color.red())
        embed.description = f"**{self.flight_data['departure']}** ({self.flight_data['dep_city']}) → **{self.flight_data['arrival']}** ({self.flight_data['arr_city']})"
        embed.add_field(name="\u200b", value=f"**✈️ Aircraft:** {self.flight_data['aircraft']}", inline=False)
        embed.add_field(name="\u200b", value=f"**🕐 Flight Time:** {self.flight_data['flight_time']}", inline=False)
        embed.add_field(name="\u200b", value=f"**🛫 Departure:** {self.flight_data['dep_time']}", inline=False)
        embed.add_field(name="\u200b", value=f"**📊 Status:** {status}", inline=False)
        embed.add_field(name="\u200b", value=f"**👨‍✈️ Pilots:** {', '.join(self.pilots)}", inline=False)
        embed.add_field(name="\u200b", value=f"**📝 Notes:** {self.flight_data.get('notes', 'No notes')}", inline=False)
        embed.set_footer(text=f"Dispatched by: <@{self.author_id}>")
        
        await interaction.message.edit(embed=embed, view=self.parent_view)
        
        if self.thread_id:
            thread = interaction.guild.get_thread(self.thread_id)
            if thread:
                await thread.send(f"**📢 Status Update**\n✈️ Flight {self.flight_data['flight']} status changed to: **{status}**\nUpdated by: {interaction.user.mention}")
        
        await interaction.response.send_message(f"✅ Flight status updated to: {status}", ephemeral=True)

class GateAssignmentModal(discord.ui.Modal, title="Assign Gates"):
    def __init__(self, pilots):
        super().__init__()
        self.pilots = pilots
        
    assignments = discord.ui.TextInput(label="Gate Assignments", placeholder="Example: MEAV001: A5, MEAV002: A6", style=discord.TextStyle.paragraph, required=True)
    
    async def on_submit(self, interaction: discord.Interaction):
        assignments_text = self.assignments.value
        await interaction.response.send_message(f"**🚪 Gate Assignments:**\n{assignments_text}", ephemeral=False)

# ==================== FLOW CLASSES (for dispatch steps) ====================

class FlightSelectView(discord.ui.View):
    def __init__(self, flight_options, departure, arrival, route_data):
        super().__init__(timeout=120)
        self.departure = departure
        self.arrival = arrival
        self.route_data = route_data
        self.add_item(FlightSelect(flight_options, departure, arrival, route_data))

class FlightSelect(discord.ui.Select):
    def __init__(self, options, departure, arrival, route_data):
        super().__init__(placeholder="Select flight number...", options=options)
        self.departure = departure
        self.arrival = arrival
        self.route_data = route_data
    
    async def callback(self, interaction: discord.Interaction):
        aircraft_options = [discord.SelectOption(label=ac, value=ac) for ac in self.route_data['aircraft']]
        aircraft_view = AircraftSelectView(aircraft_options, self.departure, self.arrival, self.values[0], self.route_data)
        await interaction.response.edit_message(content="✈️ **Select your aircraft:**", view=aircraft_view)

class AircraftSelectView(discord.ui.View):
    def __init__(self, options, departure, arrival, flight, route_data):
        super().__init__(timeout=120)
        self.departure = departure
        self.arrival = arrival
        self.flight = flight
        self.route_data = route_data
        self.add_item(AircraftSelect(options, departure, arrival, flight, route_data))

class AircraftSelect(discord.ui.Select):
    def __init__(self, options, departure, arrival, flight, route_data):
        super().__init__(placeholder="Choose aircraft...", options=options)
        self.departure = departure
        self.arrival = arrival
        self.flight = flight
        self.route_data = route_data
    
    async def callback(self, interaction: discord.Interaction):
        status_view = StatusSelectSimpleView(self.departure, self.arrival, self.flight, self.values[0], self.route_data)
        await interaction.response.edit_message(content="📊 **Select initial flight status:**", view=status_view)

class StatusSelectSimpleView(discord.ui.View):
    def __init__(self, departure, arrival, flight, aircraft, route_data):
        super().__init__(timeout=120)
        self.departure = departure
        self.arrival = arrival
        self.flight = flight
        self.aircraft = aircraft
        self.route_data = route_data
        self.add_item(StatusSelectSimple(departure, arrival, flight, aircraft, route_data))
    
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="❌ Flight dispatch cancelled.", view=None)
        self.stop()

class StatusSelectSimple(discord.ui.Select):
    def __init__(self, departure, arrival, flight, aircraft, route_data):
        super().__init__(placeholder="Choose status...", options=[
            discord.SelectOption(label="Pre-flight Check", value="Pre-flight Check"),
            discord.SelectOption(label="Taxi", value="Taxi"),
            discord.SelectOption(label="Takeoff", value="Takeoff"),
            discord.SelectOption(label="Climb", value="Climb"),
            discord.SelectOption(label="Cruise", value="Cruise"),
            discord.SelectOption(label="Descent", value="Descent"),
            discord.SelectOption(label="Landed", value="Landed"),
        ])
        self.departure = departure
        self.arrival = arrival
        self.flight = flight
        self.aircraft = aircraft
        self.route_data = route_data
    
    async def callback(self, interaction: discord.Interaction):
        modal = FlightDetailsModal(self.departure, self.arrival, self.flight, self.aircraft, self.values[0], self.route_data)
        await interaction.response.send_modal(modal)

class FlightDetailsModal(discord.ui.Modal, title="Flight Details"):
    def __init__(self, departure, arrival, flight, aircraft, status, route_data):
        super().__init__()
        self.departure = departure
        self.arrival = arrival
        self.flight = flight
        self.aircraft = aircraft
        self.status = status
        self.route_data = route_data
    
    dep_time = discord.ui.TextInput(label="Departure Time", placeholder="Example: 20:50 or 14:30", required=True)
    notes = discord.ui.TextInput(label="Flight Notes (optional)", placeholder="Any special notes about this flight...", style=discord.TextStyle.paragraph, required=False)
    
    async def on_submit(self, interaction: discord.Interaction):
        flight_data = {
            'flight': self.flight,
            'departure': self.departure,
            'dep_city': AIRPORT_INFO[self.departure]['city'],
            'arrival': self.arrival,
            'arr_city': AIRPORT_INFO[self.arrival]['city'],
            'aircraft': self.aircraft,
            'status': self.status,
            'dep_time': self.dep_time.value,
            'flight_time': self.route_data['flight_time'],
            'notes': self.notes.value or "No notes",
        }
        
        embed = discord.Embed(title=f"✈️ {self.flight} | MEAV", color=discord.Color.red())
        embed.description = f"**{self.departure}** ({flight_data['dep_city']}) → **{self.arrival}** ({flight_data['arr_city']})"
        embed.add_field(name="\u200b", value=f"**✈️ Aircraft:** {self.aircraft}", inline=False)
        embed.add_field(name="\u200b", value=f"**🕐 Flight Time:** {self.route_data['flight_time']}", inline=False)
        embed.add_field(name="\u200b", value=f"**🛫 Departure:** {self.dep_time.value}", inline=False)
        embed.add_field(name="\u200b", value=f"**📊 Status:** {self.status}", inline=False)
        embed.add_field(name="\u200b", value=f"**👨‍✈️ Pilot:** <@{interaction.user.id}>", inline=False)
        embed.add_field(name="\u200b", value=f"**📝 Notes:** {flight_data['notes']}", inline=False)
        embed.set_footer(text=f"Dispatched by: {interaction.user.display_name}")
        
        view = DispatchView(flight_data, interaction.user.id)
        
        await interaction.response.edit_message(content="✅ **Flight dispatched successfully!**", view=None, embed=None)
        await interaction.channel.send(embed=embed, view=view)

# ==================== MAIN COMMAND ====================

@bot.tree.command(name="dispatch-flight", description="Dispatch a new flight")
@app_commands.describe(departure="Departure airport (ICAO code or city name)", arrival="Arrival airport (ICAO code or city name)")
@app_commands.autocomplete(departure=departure_autocomplete, arrival=arrival_autocomplete)
async def dispatch_flight(interaction: discord.Interaction, departure: str, arrival: str):
    # Validate departure
    if departure not in AIRPORT_INFO:
        await interaction.response.send_message(f"❌ Departure airport '{departure}' not found. Please use a valid ICAO code or city name.", ephemeral=True)
        return
    
    # Validate arrival
    if arrival not in AIRPORT_INFO:
        await interaction.response.send_message(f"❌ Arrival airport '{arrival}' not found. Please use a valid ICAO code or city name.", ephemeral=True)
        return
    
    # Check if route exists
    route_key = f"{departure}_{arrival}"
    if route_key not in ROUTES:
        await interaction.response.send_message(f"❌ No direct flight found from {departure} to {arrival}.", ephemeral=True)
        return
    
    route_data = ROUTES[route_key]
    flight_options = [discord.SelectOption(label=route_data['flight'], value=route_data['flight'])]
    
    flight_view = FlightSelectView(flight_options, departure, arrival, route_data)
    await interaction.response.send_message(f"✈️ **Flight from {departure} to {arrival}**\n\nSelect your flight number:", view=flight_view, ephemeral=True)

# ==================== RUN THE BOT ====================

@bot.event
async def on_ready():
    print(f'✅ Bot is online! Logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Error syncing commands: {e}")

TOKEN = os.getenv("TOKEN")

# Simple web server to keep Render happy
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot is running')

def run_server():
    server = HTTPServer(('0.0.0.0', 10000), Handler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

bot.run(TOKEN)
