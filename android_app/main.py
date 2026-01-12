"""
TCG Meta Analyzer - Android App
Pokemon TCG competitive deck browser with matchup analysis
"""
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.clock import Clock

# Set window size for testing on desktop
Window.size = (400, 700)

# Import meta database
from meta_data import (
    META_DECKS, MATCHUPS, Language,
    get_matchup, get_deck_matchups, get_all_decks,
    get_translation, get_difficulty_translation
)


class HomeScreen(Screen):
    """Main home screen with menu options."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_language = Language.EN

        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))

        # Header
        header = Label(
            text='[b]TCG Meta Analyzer[/b]\n[size=14]Pokemon TCG Deck Browser[/size]',
            markup=True,
            size_hint_y=None,
            height=dp(80),
            halign='center',
            color=get_color_from_hex('#00BCD4')
        )
        layout.add_widget(header)

        # Language toggle
        lang_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        lang_label = Label(text='Language:', size_hint_x=0.4)
        self.lang_spinner = Spinner(
            text='English',
            values=['English', 'Portugues'],
            size_hint_x=0.6
        )
        self.lang_spinner.bind(text=self.on_language_change)
        lang_layout.add_widget(lang_label)
        lang_layout.add_widget(self.lang_spinner)
        layout.add_widget(lang_layout)

        # Menu buttons
        buttons_data = [
            ('Browse Meta Decks', 'meta'),
            ('View Matchup Chart', 'matchups'),
            ('Search Pokemon', 'search'),
            ('Deck Details', 'details'),
        ]

        for text, screen_name in buttons_data:
            btn = Button(
                text=text,
                size_hint_y=None,
                height=dp(60),
                background_color=get_color_from_hex('#2196F3'),
                font_size=dp(18)
            )
            btn.screen_name = screen_name
            btn.bind(on_press=self.go_to_screen)
            layout.add_widget(btn)

        # Spacer
        layout.add_widget(Label(size_hint_y=1))

        # Footer
        footer = Label(
            text='[size=12]January 2026 Meta[/size]',
            markup=True,
            size_hint_y=None,
            height=dp(30),
            color=get_color_from_hex('#888888')
        )
        layout.add_widget(footer)

        self.add_widget(layout)

    def on_language_change(self, spinner, text):
        self.current_language = Language.PT if text == 'Portugues' else Language.EN
        app = App.get_running_app()
        app.current_language = self.current_language

    def go_to_screen(self, button):
        self.manager.current = button.screen_name


class MetaDecksScreen(Screen):
    """Screen showing top 8 meta decks."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        # Header with back button
        header = BoxLayout(size_hint_y=None, height=dp(50))
        back_btn = Button(text='< Back', size_hint_x=0.3)
        back_btn.bind(on_press=self.go_back)
        header.add_widget(back_btn)
        header.add_widget(Label(text='[b]Top 8 Meta Decks[/b]', markup=True))
        layout.add_widget(header)

        # Scrollable deck list
        scroll = ScrollView()
        self.deck_grid = GridLayout(cols=1, spacing=dp(10), size_hint_y=None)
        self.deck_grid.bind(minimum_height=self.deck_grid.setter('height'))

        scroll.add_widget(self.deck_grid)
        layout.add_widget(scroll)

        self.add_widget(layout)

    def on_enter(self):
        """Called when screen is displayed."""
        self.refresh_decks()

    def refresh_decks(self):
        self.deck_grid.clear_widgets()
        lang = App.get_running_app().current_language

        for i, deck in enumerate(get_all_decks()[:8], 1):
            deck_btn = Button(
                text=f"{i}. {deck.get_name(lang)}\n"
                     f"Tier {deck.tier} | {deck.meta_share:.1f}% | {get_difficulty_translation(deck.difficulty, lang)}",
                size_hint_y=None,
                height=dp(80),
                halign='left',
                valign='middle',
                text_size=(dp(350), None),
                background_color=self.get_tier_color(deck.tier)
            )
            deck_btn.deck_id = deck.id
            deck_btn.bind(on_press=self.show_deck_details)
            self.deck_grid.add_widget(deck_btn)

    def get_tier_color(self, tier):
        colors = {
            1: get_color_from_hex('#4CAF50'),  # Green
            2: get_color_from_hex('#FFC107'),  # Amber
            3: get_color_from_hex('#9E9E9E'),  # Gray
        }
        return colors.get(tier, get_color_from_hex('#2196F3'))

    def show_deck_details(self, button):
        app = App.get_running_app()
        app.selected_deck_id = button.deck_id
        self.manager.current = 'details'

    def go_back(self, *args):
        self.manager.current = 'home'


class DeckDetailsScreen(Screen):
    """Screen showing detailed deck information."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(5))

        # Header with back button
        header = BoxLayout(size_hint_y=None, height=dp(50))
        back_btn = Button(text='< Back', size_hint_x=0.3)
        back_btn.bind(on_press=self.go_back)
        header.add_widget(back_btn)
        self.title_label = Label(text='[b]Deck Details[/b]', markup=True)
        header.add_widget(self.title_label)
        layout.add_widget(header)

        # Tabbed content
        self.tabs = TabbedPanel(do_default_tab=False)

        # Info tab
        self.info_tab = TabbedPanelItem(text='Info')
        self.info_scroll = ScrollView()
        self.info_content = Label(
            text='',
            markup=True,
            size_hint_y=None,
            halign='left',
            valign='top',
            text_size=(dp(360), None)
        )
        self.info_content.bind(texture_size=self.info_content.setter('size'))
        self.info_scroll.add_widget(self.info_content)
        self.info_tab.add_widget(self.info_scroll)
        self.tabs.add_widget(self.info_tab)

        # Deck List tab
        self.list_tab = TabbedPanelItem(text='Cards')
        self.list_scroll = ScrollView()
        self.list_content = Label(
            text='',
            markup=True,
            size_hint_y=None,
            halign='left',
            valign='top',
            font_size=dp(12),
            text_size=(dp(360), None)
        )
        self.list_content.bind(texture_size=self.list_content.setter('size'))
        self.list_scroll.add_widget(self.list_content)
        self.list_tab.add_widget(self.list_scroll)
        self.tabs.add_widget(self.list_tab)

        # Matchups tab
        self.matchups_tab = TabbedPanelItem(text='Matchups')
        self.matchups_scroll = ScrollView()
        self.matchups_content = Label(
            text='',
            markup=True,
            size_hint_y=None,
            halign='left',
            valign='top',
            text_size=(dp(360), None)
        )
        self.matchups_content.bind(texture_size=self.matchups_content.setter('size'))
        self.matchups_scroll.add_widget(self.matchups_content)
        self.matchups_tab.add_widget(self.matchups_scroll)
        self.tabs.add_widget(self.matchups_tab)

        layout.add_widget(self.tabs)
        self.add_widget(layout)

    def on_enter(self):
        """Called when screen is displayed."""
        app = App.get_running_app()
        deck_id = getattr(app, 'selected_deck_id', None)

        if deck_id and deck_id in META_DECKS:
            self.show_deck(META_DECKS[deck_id])

    def show_deck(self, deck):
        lang = App.get_running_app().current_language

        # Update title
        self.title_label.text = f'[b]{deck.get_name(lang)}[/b]'

        # Info tab content
        diff_color = {'Beginner': '4CAF50', 'Intermediate': 'FFC107', 'Advanced': 'F44336'}
        diff = deck.difficulty
        color = diff_color.get(diff, 'FFFFFF')

        strengths = '\n'.join([f"  [color=4CAF50]+[/color] {s}" for s in deck.get_strengths(lang)])
        weaknesses = '\n'.join([f"  [color=F44336]-[/color] {w}" for w in deck.get_weaknesses(lang)])

        info_text = f"""[b][size=18]{deck.get_name(lang)}[/size][/b]

[b]Tier:[/b] {deck.tier}
[b]Meta Share:[/b] {deck.meta_share:.1f}%
[b]Difficulty:[/b] [color={color}]{get_difficulty_translation(diff, lang)}[/color]

[b]{get_translation('description', lang) if lang == Language.PT else 'Description'}:[/b]
{deck.get_description(lang)}

[b]{get_translation('strategy', lang)}:[/b]
{deck.get_strategy(lang)}

[b]Key Pokemon:[/b] {', '.join(deck.key_pokemon)}
[b]Energy:[/b] {', '.join(deck.energy_types)}

[b]{get_translation('strengths', lang)}:[/b]
{strengths}

[b]{get_translation('weaknesses', lang)}:[/b]
{weaknesses}
"""
        self.info_content.text = info_text

        # Deck list tab content
        pokemon = deck.get_pokemon()
        trainers = deck.get_trainers()
        energy = deck.get_energy()

        pokemon_text = '\n'.join([f"  {c.quantity} {c.get_name(lang)} {c.set_code} {c.set_number}" for c in pokemon])
        trainer_text = '\n'.join([f"  {c.quantity} {c.get_name(lang)} {c.set_code} {c.set_number}" for c in trainers])
        energy_text = '\n'.join([f"  {c.quantity} {c.get_name(lang)} {c.set_code} {c.set_number}" for c in energy])

        list_text = f"""[b]Pokemon ({sum(c.quantity for c in pokemon)}):[/b]
{pokemon_text}

[b]{get_translation('trainer', lang)} ({sum(c.quantity for c in trainers)}):[/b]
{trainer_text}

[b]{get_translation('energy', lang)} ({sum(c.quantity for c in energy)}):[/b]
{energy_text}

[b]Total: {deck.total_cards()} cards[/b]
"""
        self.list_content.text = list_text

        # Matchups tab content
        matchups = get_deck_matchups(deck.id)
        matchup_lines = []

        for opp_id, win_rate, notes in matchups:
            opp_deck = META_DECKS.get(opp_id)
            if opp_deck:
                if win_rate >= 55:
                    color = '4CAF50'
                    status = get_translation('favored', lang)
                elif win_rate <= 45:
                    color = 'F44336'
                    status = get_translation('unfavored', lang)
                else:
                    color = 'FFC107'
                    status = get_translation('even', lang)

                matchup = get_matchup(deck.id, opp_id)
                notes_text = matchup.get_notes(lang) if matchup else ""

                matchup_lines.append(
                    f"[b]vs {opp_deck.get_name(lang)}[/b]\n"
                    f"  [color={color}]{win_rate:.0f}%[/color] - {status}\n"
                    f"  [size=11]{notes_text}[/size]\n"
                )

        matchups_text = f"[b]{get_translation('matchups', lang)}:[/b]\n\n" + '\n'.join(matchup_lines)
        self.matchups_content.text = matchups_text

    def go_back(self, *args):
        self.manager.current = 'meta'


class MatchupsScreen(Screen):
    """Screen showing matchup matrix."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        # Header with back button
        header = BoxLayout(size_hint_y=None, height=dp(50))
        back_btn = Button(text='< Back', size_hint_x=0.3)
        back_btn.bind(on_press=self.go_back)
        header.add_widget(back_btn)
        header.add_widget(Label(text='[b]Matchup Chart[/b]', markup=True))
        layout.add_widget(header)

        # Instructions
        instructions = Label(
            text='Select two decks to compare:',
            size_hint_y=None,
            height=dp(30)
        )
        layout.add_widget(instructions)

        # Deck selectors
        selector_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))

        decks = get_all_decks()[:8]
        deck_names = [d.name_en for d in decks]

        self.deck_a_spinner = Spinner(
            text='Select Deck 1',
            values=deck_names
        )
        self.deck_b_spinner = Spinner(
            text='Select Deck 2',
            values=deck_names
        )

        selector_layout.add_widget(self.deck_a_spinner)
        selector_layout.add_widget(self.deck_b_spinner)
        layout.add_widget(selector_layout)

        # Compare button
        compare_btn = Button(
            text='Compare',
            size_hint_y=None,
            height=dp(50),
            background_color=get_color_from_hex('#4CAF50')
        )
        compare_btn.bind(on_press=self.compare_decks)
        layout.add_widget(compare_btn)

        # Result area
        self.result_scroll = ScrollView()
        self.result_label = Label(
            text='',
            markup=True,
            size_hint_y=None,
            halign='left',
            valign='top',
            text_size=(dp(360), None)
        )
        self.result_label.bind(texture_size=self.result_label.setter('size'))
        self.result_scroll.add_widget(self.result_label)
        layout.add_widget(self.result_scroll)

        # Legend
        legend = Label(
            text='[color=4CAF50]Green[/color]=Favored (55%+)  '
                 '[color=FFC107]Yellow[/color]=Even  '
                 '[color=F44336]Red[/color]=Unfavored',
            markup=True,
            size_hint_y=None,
            height=dp(40),
            font_size=dp(11)
        )
        layout.add_widget(legend)

        self.add_widget(layout)

    def compare_decks(self, *args):
        lang = App.get_running_app().current_language

        deck_a_name = self.deck_a_spinner.text
        deck_b_name = self.deck_b_spinner.text

        if deck_a_name == 'Select Deck 1' or deck_b_name == 'Select Deck 2':
            self.result_label.text = '[color=F44336]Please select both decks[/color]'
            return

        if deck_a_name == deck_b_name:
            self.result_label.text = '[color=F44336]Please select different decks[/color]'
            return

        # Find deck IDs
        deck_a = None
        deck_b = None
        for deck in META_DECKS.values():
            if deck.name_en == deck_a_name:
                deck_a = deck
            if deck.name_en == deck_b_name:
                deck_b = deck

        if not deck_a or not deck_b:
            self.result_label.text = '[color=F44336]Deck not found[/color]'
            return

        matchup = get_matchup(deck_a.id, deck_b.id)
        if not matchup:
            self.result_label.text = '[color=FFC107]No matchup data available[/color]'
            return

        # Determine colors
        if matchup.win_rate_a >= 55:
            color_a = '4CAF50'
            color_b = 'F44336'
        elif matchup.win_rate_a <= 45:
            color_a = 'F44336'
            color_b = '4CAF50'
        else:
            color_a = 'FFC107'
            color_b = 'FFC107'

        result_text = f"""[b][size=18]Matchup Analysis[/size][/b]

[b]{deck_a.get_name(lang)}[/b]
vs
[b]{deck_b.get_name(lang)}[/b]

[size=24][color={color_a}]{matchup.win_rate_a:.0f}%[/color][/size] - [size=24][color={color_b}]{matchup.win_rate_b:.0f}%[/color][/size]

[b]{get_translation('notes', lang)}:[/b]
{matchup.get_notes(lang)}

[b]Deck A Strengths:[/b]
{chr(10).join(['  + ' + s for s in deck_a.get_strengths(lang)[:3]])}

[b]Deck B Strengths:[/b]
{chr(10).join(['  + ' + s for s in deck_b.get_strengths(lang)[:3]])}
"""
        self.result_label.text = result_text

    def go_back(self, *args):
        self.manager.current = 'home'


class SearchScreen(Screen):
    """Screen for searching Pokemon in meta decks."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        # Header with back button
        header = BoxLayout(size_hint_y=None, height=dp(50))
        back_btn = Button(text='< Back', size_hint_x=0.3)
        back_btn.bind(on_press=self.go_back)
        header.add_widget(back_btn)
        header.add_widget(Label(text='[b]Search Pokemon[/b]', markup=True))
        layout.add_widget(header)

        # Search input
        search_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        self.search_input = TextInput(
            hint_text='Enter Pokemon name...',
            multiline=False,
            size_hint_x=0.7
        )
        search_btn = Button(
            text='Search',
            size_hint_x=0.3,
            background_color=get_color_from_hex('#4CAF50')
        )
        search_btn.bind(on_press=self.do_search)
        search_layout.add_widget(self.search_input)
        search_layout.add_widget(search_btn)
        layout.add_widget(search_layout)

        # Results
        self.result_scroll = ScrollView()
        self.result_grid = GridLayout(cols=1, spacing=dp(10), size_hint_y=None)
        self.result_grid.bind(minimum_height=self.result_grid.setter('height'))
        self.result_scroll.add_widget(self.result_grid)
        layout.add_widget(self.result_scroll)

        self.add_widget(layout)

    def do_search(self, *args):
        query = self.search_input.text.strip().lower()
        if not query:
            return

        self.result_grid.clear_widgets()
        lang = App.get_running_app().current_language

        found = False
        for deck in META_DECKS.values():
            # Check key pokemon
            for key_mon in deck.key_pokemon:
                if query in key_mon.lower():
                    self.add_result(deck, lang, f"Key Pokemon: {key_mon}")
                    found = True
                    break
            else:
                # Check all cards
                for card in deck.cards:
                    if card.card_type == "pokemon" and query in card.name_en.lower():
                        self.add_result(deck, lang, f"Contains: {card.name_en}")
                        found = True
                        break

        if not found:
            self.result_grid.add_widget(
                Label(
                    text=f'No meta decks found with "{query}"',
                    size_hint_y=None,
                    height=dp(50)
                )
            )

    def add_result(self, deck, lang, reason):
        btn = Button(
            text=f"{deck.get_name(lang)}\n{reason}\nTier {deck.tier} | {deck.meta_share:.1f}%",
            size_hint_y=None,
            height=dp(80),
            halign='left',
            valign='middle',
            text_size=(dp(350), None),
            background_color=get_color_from_hex('#2196F3')
        )
        btn.deck_id = deck.id
        btn.bind(on_press=self.show_deck)
        self.result_grid.add_widget(btn)

    def show_deck(self, button):
        app = App.get_running_app()
        app.selected_deck_id = button.deck_id
        self.manager.current = 'details'

    def go_back(self, *args):
        self.manager.current = 'home'


class TCGMetaApp(App):
    """Main application class."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_language = Language.EN
        self.selected_deck_id = None

    def build(self):
        self.title = 'TCG Meta Analyzer'

        # Screen manager
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(MetaDecksScreen(name='meta'))
        sm.add_widget(DeckDetailsScreen(name='details'))
        sm.add_widget(MatchupsScreen(name='matchups'))
        sm.add_widget(SearchScreen(name='search'))

        return sm


if __name__ == '__main__':
    TCGMetaApp().run()
