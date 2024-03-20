from interactions import (
    Embed,
    Extension,
    Message,
    OptionType,
    SlashCommandChoice,
    SlashContext,
    slash_command,
    slash_option,
)
from app.library.initiativatracking import InitiativeTracking,insert_after_name,insert_before_index,insert_before_name, remove_from_initiative,set_channel_initiative,remove_channel_initiative,get_channel_initiative,insert_channel_message


class InitiativeTracker(Extension):
    
    async def async_start(self):
        print("Starting InitiativeTracker Extension")

    @slash_command(
        name='initiative_help',
        description='shows help for the commands about initiatve tracking'
    )
    async def initiative_help(self,ctx:SlashContext):
        await ctx.send('''
**Initiative Tracking**
You can start a List for initiative by providing a list of ordered participants in the /initiative command. The Participants need to be seperated by comma
                       
Or by inserting a name or two with:
* /initiative_insert_before
* /initiative_insert_after
* /initiative_insert_first
* /initiative_insert_last
You can also use these 4 commands to change the order.

With /initiative_remove you can remove one participant from the list

With /initiative_delete you can delete the complete list
                       
Use /initiative_show to just refresh the message
'''
        )

    @slash_command( name='initiative',
        description='start initiative tracking in this channel'
    )
    @slash_option( name='participants',
        description='you can provide an initial ordered list of names e.g. Robin,Alex,NPC1',
        required=False,
        opt_type=OptionType.STRING
    )
    async def start_initiative(self,ctx:SlashContext,participants:str=""):
        channel_id:str = str(ctx.channel_id)
        if existing_trackings := get_channel_initiative(channel_id):
            if old_message := ctx.channel.get_message(
                existing_trackings[0].message_id
            ):
                await ctx.channel.delete_message(old_message)
        set_channel_initiative(channel_id,*[name.strip() for name in participants.split(',') if name])
        await show_channel_initiative(ctx)


    @slash_command( name='initiative_show',
        description='shows the initiative list without changing it')
    async def show_initiative(self,ctx:SlashContext):
        channel_id:str = str(ctx.channel_id)
        trackings = get_channel_initiative(channel_id)
        await ctx.send( embed = render_initiative([tracking.name for tracking in trackings]))


    @slash_command( name='initiative_insert_before',
        description='adds or moves a participant before another participant'
    )
    @slash_option(name='name',description='name of moved or inserted participant',opt_type=OptionType.STRING)
    @slash_option(name='name_after',description='name to add before',opt_type=OptionType.STRING)
    async def insert_before(self,ctx:SlashContext,name:str,name_after:str):
        channel_id:str = str(ctx.channel_id)
        if not get_channel_initiative(channel_id):
            set_channel_initiative(channel_id,name.strip(),name_after.strip())
        else:
            insert_before_name(channel_id,name_after.strip(),name.strip())
        await show_channel_initiative(ctx)

    @slash_command( name='initiative_insert_after',
        description='adds or moves a participant after another participant'
    )
    @slash_option(name='name',description='name of moved or inserted participant',opt_type=OptionType.STRING)
    @slash_option(name='name_before',description='name to add after',opt_type=OptionType.STRING)
    async def insert_after(self,ctx:SlashContext,name:str,name_before:str):
        channel_id:str = str(ctx.channel_id)
        if not get_channel_initiative(channel_id):
            set_channel_initiative(channel_id,name_before.strip(),name.strip())
        else:
            insert_after_name(channel_id,name_before.strip(),name.strip())
        await show_channel_initiative(ctx)

    @slash_command( name='initiative_insert_first',
        description='adds or moves a participant at first place'
    )
    @slash_option(name='name',description='name of moved or inserted participant',opt_type=OptionType.STRING)
    async def insert_after(self,ctx:SlashContext,name:str):
        channel_id:str = str(ctx.channel_id)
        if not get_channel_initiative(channel_id):
            set_channel_initiative(channel_id,name.strip())
        else:
            insert_before_index(channel_id,0,name.strip())
        await show_channel_initiative(ctx)

    @slash_command( name='initiative_insert_last',
        description='adds or moves a participant at first place'
    )
    @slash_option(name='name',description='name of moved or inserted participant',opt_type=OptionType.STRING)
    async def insert_after(self,ctx:SlashContext,name:str):
        channel_id:str = str(ctx.channel_id)
        if existing := get_channel_initiative(channel_id):
            insert_before_index(channel_id,existing[-1].initiative_order+1,name.strip())
        else:
            set_channel_initiative(channel_id,name.strip())
        await show_channel_initiative(ctx)

    @slash_command( name='initiative_remove',
        description='remove one participant from initiative order'
    )
    @slash_option(name='name',description='name of participant to remove',opt_type=OptionType.STRING)
    async def remove_name(self,ctx:SlashContext, name:str):
        channel_id:str = str(ctx.channel_id)
        remove_from_initiative(channel_id,name.strip())
        await show_channel_initiative(ctx,True)

    @slash_command( name='initiative_delete',
        description='deletes the initiative tracking')
    @slash_option(name='confirmation',description='type YES to confirm deletion',opt_type=OptionType.STRING)
    async def delete_initiative(self,ctx:SlashContext,confirmation:str):
        if confirmation != 'YES':
            await ctx.send('you need to say YES (all caps) to confirm deletion',ephemeral=True)
            return
        
        channel_id:str = str(ctx.channel_id)
        if existing_trackings := get_channel_initiative(channel_id):
            if old_message := ctx.channel.get_message(
                existing_trackings[0].message_id
            ):
                await ctx.channel.delete_message(old_message)
        remove_channel_initiative(channel_id)
        await ctx.send('initiative removed')

async def show_channel_initiative(ctx:SlashContext,refresh_message:bool=False):
    channel_id:str = str(ctx.channel_id)
    trackings = get_channel_initiative(channel_id)
    names = [tracking.name for tracking in trackings]
    if refresh_message and trackings:
        if old_message := ctx.channel.get_message(
            trackings[0].message_id
        ):
            await ctx.channel.delete_message(old_message)
            return
    new_message = await ctx.send(embed=render_initiative(names))
    insert_channel_message(channel_id,str(new_message.id))

def render_initiative(names:list[str]):
    return Embed(
        title='Initiative Tracker',
        description='\n'.join(names) if names else 'EMPTY -> use insert commands to fill the slots'
    )