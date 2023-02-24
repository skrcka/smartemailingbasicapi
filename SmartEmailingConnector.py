import aiohttp

from ContactList import ContactList


class SmartEmailingConnector:
    def __init__(self, username, api_key, source_email):
        self.username = username
        self.api_key = api_key
        self.api_url = 'https://app.smartemailing.cz/api/v3/'
        self.headers = {
                'Content-Type': 'application/json',
            }
        self.auth = aiohttp.BasicAuth(self.username, password=self.api_key)
        self.default_contact_list = ContactList('mentortools', 'mentortools', source_email, source_email)

    async def check_api_status(self):
        async with aiohttp.ClientSession() as session:
            url = self.api_url + 'ping'
            async with session.get(url, headers=self.headers) as response:
                response_data = await response.json()
                if response.status == 200:
                    return response_data['message']
                else:
                    raise Exception(response_data['message'])

    async def check_credentials(self):
        async with aiohttp.ClientSession() as session:
            url = self.api_url + 'check-credentials'
            async with session.post(url, headers=self.headers, auth=self.auth) as response:
                response_data = await response.json()
                if response.status == 200:
                    return response_data['message']
                else:
                    raise Exception(response_data['message'])

    async def get_contact_lists(self, name = None):
        url = self.api_url + 'contactlists'
        if name:
            url += f'?name={name}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers, auth=self.auth) as response:
                response_data = await response.json()
                if response.status == 200:
                    return response_data['data']
                else:
                    raise Exception(response_data['message'])

    async def get_contact_list(self, id):
        url = self.api_url + 'contactlists' + f'/{id}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers, auth=self.auth) as response:
                response_data = await response.json()
                if response.status == 200:
                    return response_data['data']
                else:
                    raise Exception(response_data['message'])

    async def get_contacts(self, email: str = None):
        url = self.api_url + 'contacts' + f'?emailaddress={email}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers, auth=self.auth) as response:
                response_data = await response.json()
                if response.status == 200:
                    return response_data['data']
                else:
                    raise Exception(response_data['message'])

    async def update_contact_list(self, contactlist: ContactList):
        payload = contactlist.__dict__.copy()
        payload.pop('id')
        if not contactlist.id:
            contactlist.id = self.get_contact_lists(contactlist.name)[0]['id']
        url = self.api_url + 'contactlists' + f'/{contactlist.id}'
        async with aiohttp.ClientSession() as session:
            async with session.put(url, headers=self.headers, json=payload, auth=self.auth) as response:
                response_data = await response.json()
                if response.status == 200:
                    return response_data['data']
                else:
                    raise Exception(response_data['message'])

    async def create_contact_list(self, contactlist: ContactList):
        payload = contactlist.__dict__.copy()
        payload.pop('id')
        url = self.api_url + 'contactlists'
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=self.headers, json=payload, auth=self.auth) as response:
                response_data = await response.json()
                if response.status == 201:
                    data = response_data['data']
                    contactlist.id = data['id']
                    return data
                else:
                    raise Exception(response_data['message'])

    async def add_contact(self, name, email):
        contactlist = await self.get_contact_lists(self.default_contact_list.name)
        if not contactlist:
            await self.create_contact_list(self.default_contact_list)
            id = self.default_contact_list.id
        else:
            id = contactlist[0]['id']
        
        payload = {
            'settings': {
                "update": True,
            },
            'data': [{
                'emailaddress': email,
                'name': name,
                'contactlists': [
                    {
                        'id': id,
                        'status': 'confirmed'
                    }
                ],
                }
            ],
        }
        async with aiohttp.ClientSession() as session:
            url = self.api_url + 'import'
            async with session.post(url, headers=self.headers, json=payload, auth=self.auth) as response:
                response_data = await response.json()
                if response.status == 201:
                    response = response_data['contacts_map'][0]
                    return response
                else:
                    raise Exception(response_data['message'])

    async def add_tag(self, email, tag):
        contactlists = await self.get_contact_lists()
        tags = [contactlist['name'] for contactlist in contactlists]
        if tag not in tags:
            cl = ContactList(tag, tag, self.default_contact_list.sendername, self.default_contact_list.senderemail)
            await self.create_contact_list(cl)
            cid = cl.id
        else:
            cid = contactlists[tags.index(tag)]['id']

        contactlists_payload = []
        contact = await self.get_contacts(email)
        contact = contact[0]
        contact_contactlist = contact['contactlists']
        for c in contact_contactlist:
            contactlists_payload.append({'id': c['contactlist_id'], 'status': c['status']})
        contactlists_payload.append({'id': cid, 'status': 'confirmed'})

        payload = {
            'settings': {
                "update": True,
            },
            'data': [{
                'emailaddress': email,
                'name': contact['name'],
                'contactlists': contactlists_payload
                }
            ],
        }

        async with aiohttp.ClientSession() as session:
            url = self.api_url + 'import'
            async with session.post(url, headers=self.headers, json=payload, auth=self.auth) as response:
                response_data = await response.json()
                if response.status == 201:
                    response = response_data['contacts_map'][0]
                    return response
                else:
                    raise Exception(response_data['message'])

