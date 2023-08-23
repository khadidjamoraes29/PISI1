from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
import firebase_admin
from firebase_admin import credentials, db
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivy.core.window import Window
from kivy.uix.button import Button


Window.size = (350, 580)

class HomeScreen(Screen):
    def goto_auth_screen(self, user_type):
        app = MDApp.get_running_app()
        auth_screen = app.root.get_screen('auth')
        auth_screen.set_user_type(user_type)
        app.root.current = 'auth'

class AuthScreen(Screen):
    def __init__(self, user_type, **kwargs):
        super(AuthScreen, self).__init__(**kwargs)
        self.user_type = user_type
        self.authenticated_username = None

    def set_user_type(self, user_type):
        self.user_type = user_type
        self.set_title()

    def set_title(self):
        self.ids.title_label.text = f"Cadastro e Login"

    def initialize_firebase(self):
        try:
            cred = credentials.Certificate("upconsult-3cbc7-firebase-adminsdk-z8ctc-977a829468.json")
            firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://upconsult-3cbc7-default-rtdb.firebaseio.com'
            })

        except:
            raise(ValueError)

    def register(self):
        username = self.ids.username_input.text
        password = self.ids.password_input.text

        if not username or not password:
            print("Preencha todos os campos!")
            return

        self.initialize_firebase()

        user_type_lower = self.user_type.lower()
        users_ref = db.reference(user_type_lower)
        users_ref.child(username).set({
            'password': password,
            'username': username
        })

        print(f"Usuário {username} cadastrado com senha {password}")

    def login(self):
        username = self.ids.username_input.text
        password = self.ids.password_input.text 

        if not username or not password:
            print("Preencha todos os campos!")
            return

        self.initialize_firebase()

        user_type_lower = self.user_type.lower()
        users_ref = db.reference(user_type_lower)
        user_data = users_ref.child(username).get()

        if user_data is not None and user_data.get("password") == password:
            print(f"Usuário {username} logado com sucesso!")
            self.authenticated_username = username
            self.manager.current = 'services'

        else:
            print("Usuário ou senha inválidos")
            print(f"Detalhes do erro: {user_data}")   

class ServicesScreen(Screen):
    solicitacao_values = {}

    def go_to_services(self, instance):
        self.manager.current = 'services'

    def go_to_perfil(self, instance):
        self.manager.current = 'perfil'
        
    def go_to_solicitacao(self, instance):
        self.manager.current = 'solicitacao'

    def go_to_agendamento(self, instance):

        # Passa os valores da solicitação para a tela de agendamento
        agendamento_screen = self.manager.get_screen('agendamento')
        agendamento_screen.show_solicitacao(**self.solicitacao_values)
        self.solicitacao_values = {}

        self.manager.current = 'agendamento'
        
    def go_to_procurar(self, instance):
        procurar_screen = self.manager.get_screen('procurar')
        procurar_screen.pesquisa()
        self.manager.current = 'procurar'

class PerfilScreen(Screen):
    pass

class SolicitacaoScreen(Screen):
    # Dentro da função enviar_solicitacao da classe SolicitacaoScreen
    def enviar_solicitacao(self):
        tipo_consultoria = self.ids.tipo_consultoria.text
        descricao = self.ids.descricao.text
        data_agendamento = self.ids.data_agendamento.text

        if tipo_consultoria and descricao and data_agendamento:
            # Recupere o username do usuário atual (você deve ter essa informação após o login)
            username = self.manager.get_screen('auth').authenticated_username

            # Acesse o nó correspondente ao usuário no banco de dados
            user_ref = db.reference(f'empresa/{username}/solicitacoes')

            # Crie um novo nó para a solicitação
            new_request_ref = user_ref.push()
            new_request_ref.set({
                'tipo_consultoria': tipo_consultoria,
                'descricao': descricao,
                'data_agendamento': str(data_agendamento)  # Converta para string ou use um formato específico
            })

            services_screen = self.manager.get_screen('services')
            services_screen.solicitacao_values = {
                'tipo_consultoria': tipo_consultoria,
                'descricao': descricao,
                'data_agendamento': data_agendamento
            }

            print("Solicitação enviada com sucesso!")
        else:
            print("Preencha todos os campos!")


        # Limpar os campos após enviar a solicitação
        self.ids.tipo_consultoria.text = ""
        self.ids.descricao.text = ""
        self.ids.data_agendamento.date = ""


class AgendamentoScreen(Screen):
    def show_solicitacao(self, tipo_consultoria, descricao, data_agendamento):
        
        self.ids.tipo_consultoria_label.text = f"Tipo de Consultoria: {tipo_consultoria}"
        self.ids.descricao_label.text = f"Descrição: {descricao}"
        self.ids.data_agendamento_label.text = f"Data de Agendamento: {data_agendamento}"


class ProcurarScreen(Screen):
   
    def pesquisa(self):
        usert = "Consultor"
        users_ref2 = db.reference(usert)
        user_data2 = users_ref2.get()

        if user_data2 is not None:
            consultor_data = user_data2.get("NomeConsultor")
            print (consultor_data)
            telefoneConsultor = user_data2.get("Telefone")
            print (telefoneConsultor)
            enderecoConsultor = user_data2.get("Endereço")
            print (enderecoConsultor)

            self.ids.consultor_label.text = f"Consultor: \n{consultor_data}"
            self.ids.telefoneConsultor_label.text = f"Telefone do Consultor: \n{telefoneConsultor}"
            self.ids.enderecoConsultor_label.text = f"Endereço do Consultor: \n{enderecoConsultor}"
        
        else:
            print ('Está vazio a solicitação')

class RegistrationApp(MDApp):
    def build(self):
        self.screen_manager = ScreenManager()

        self.home_screen = HomeScreen(name='home')
        self.auth_screen = AuthScreen(name='auth', user_type='Empresa')  # Defina o tipo de usuário desejado aqui
        self.services_screen = ServicesScreen(name='services')
        self.perfil_screen = PerfilScreen(name='perfil')
        self.solicitacao_screen = SolicitacaoScreen(name='solicitacao')
        self.agendamento_screen = AgendamentoScreen(name='agendamento')
        self.procurar_screen = ProcurarScreen(name='procurar')

        self.screen_manager.add_widget(self.home_screen)
        self.screen_manager.add_widget(self.auth_screen)
        self.screen_manager.add_widget(self.services_screen)
        self.screen_manager.add_widget(self.perfil_screen)
        self.screen_manager.add_widget(self.solicitacao_screen)
        self.screen_manager.add_widget(self.agendamento_screen)
        self.screen_manager.add_widget(self.procurar_screen)

        return self.screen_manager

    def on_start(self):
        Builder.load_file('registration.kv')

if __name__ == '__main__':
    RegistrationApp().run()



