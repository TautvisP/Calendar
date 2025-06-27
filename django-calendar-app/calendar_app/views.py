import calendar
from django.contrib import messages
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Person, Event, EventTag, PersonRole
from .forms import ClientRegisterForm, PersonRegistrationForm, EventForm, ProfileForm, EventTagForm, CustomPasswordChangeForm, ClientLoginForm, PersonRoleForm
from django.contrib.auth import login, logout, update_session_auth_hash


# Person Views
class PersonListView(LoginRequiredMixin, View):
    def get(self, request):
        people = Person.objects.filter(client=request.user)
        return render(request, 'calendar_app/person_list.html', {
            'people': people,
            'edit_person_id': None,
            'edit_person_form': None,
        })

    def post(self, request):
        people = Person.objects.filter(client=request.user)
        edit_person_id = request.POST.get('edit_person_id')
        edit_person_form = None

        if 'edit_person' in request.POST and edit_person_id:
            person = Person.objects.get(id=edit_person_id, client=request.user)
            edit_person_form = PersonRegistrationForm(instance=person, user=request.user)
            return render(request, 'calendar_app/person_list.html', {
                'people': people,
                'edit_person_id': int(edit_person_id),
                'edit_person_form': edit_person_form,
            })
        elif 'save_person' in request.POST and edit_person_id:
            person = Person.objects.get(id=edit_person_id, client=request.user)
            edit_person_form = PersonRegistrationForm(request.POST, instance=person, user=request.user)

            if edit_person_form.is_valid():
                edit_person_form.save()
                messages.success(request, "Žmogaus informacija sėkmingai atnaujinta.")
                return redirect('person_list')
            return render(request, 'calendar_app/person_list.html', {
                'people': people,
                'edit_person_id': int(edit_person_id),
                'edit_person_form': edit_person_form,
            })
        elif 'delete_person' in request.POST and request.POST.get('delete_person_id'):
            person = Person.objects.get(id=request.POST.get('delete_person_id'), client=request.user)
            person.delete()
            messages.success(request, "Žmogus ištrintas sėkmingai.")
            return redirect('person_list')

        return render(request, 'calendar_app/person_list.html', {
            'people': people,
            'edit_person_id': None,
            'edit_person_form': None,
        })


class PersonCreateView(LoginRequiredMixin, CreateView):
    model = Person
    form_class = PersonRegistrationForm
    template_name = 'calendar_app/person_registration.html'
    success_url = reverse_lazy('person_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.client = self.request.user
        return super().form_valid(form)


# Event Views
class EventCreateView(LoginRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = 'calendar_app/event_form.html'
    success_url = reverse_lazy('calendar')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.client = self.request.user
        if not form.cleaned_data.get('person') and not (form.cleaned_data.get('manual_name') and form.cleaned_data.get('manual_surname')):
            form.add_error(None, "Pasirinkite žmogų iš sąrašo arba įveskite jo duomenis ranka.")
            return self.form_invalid(form)
        return super().form_valid(form)



class EventDetailView(LoginRequiredMixin, DetailView):
    model = Event
    template_name = 'calendar_app/event_detail.html'
    context_object_name = 'event'

    def get_queryset(self):
        return Event.objects.filter(client=self.request.user)



# Calendar View
class CalendarView(LoginRequiredMixin, TemplateView):
    template_name = 'calendar_app/calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        year = int(self.request.GET.get('year', today.year))
        month = int(self.request.GET.get('month', today.month))
        week_num = int(self.request.GET.get('week', today.isocalendar()[1]))

        lt_month_names = [
            "",
            "Sausis", "Vasaris", "Kovas", "Balandis", "Gegužė", "Birželis",
            "Liepa", "Rugpjūtis", "Rugsėjis", "Spalis", "Lapkritis", "Gruodis"
        ]

        cal = calendar.Calendar(firstweekday=0)
        month_days = []
        week_list = []
        for week in cal.monthdatescalendar(year, month):
            week_days = []
            for day in week:
                events = Event.objects.filter(date=day, client=self.request.user)
                week_days.append({
                    'day': day.day,
                    'date': day,
                    'in_month': day.month == month,
                    'events': events,
                })
            iso_week = week[0].isocalendar()[1]
            is_current_week = iso_week == week_num
            month_days.append({'days': week_days, 'is_current_week': is_current_week, 'iso_week': iso_week})
            week_list.append(iso_week)

        week_list = sorted(set(week_list))
        if week_num not in week_list:
            week_num = week_list[0]
        week_idx = week_list.index(week_num)
        prev_week = week_list[week_idx - 1] if week_idx > 0 else week_list[0]
        next_week = week_list[week_idx + 1] if week_idx < len(week_list) - 1 else week_list[-1]

        current_week_obj = next((w for w in month_days if w['iso_week'] == week_num), month_days[0])
        first_day = current_week_obj['days'][0]['date']
        last_day = current_week_obj['days'][-1]['date']
        week_range_str = f"{lt_month_names[first_day.month]} {first_day.day}-{last_day.day}"

        prev_month = month - 1 if month > 1 else 12
        prev_year = year if month > 1 else year - 1
        next_month = month + 1 if month < 12 else 1
        next_year = year if month < 12 else year + 1

        lt_day_abbr = ["Pr", "An", "Tr", "Kt", "Pn", "Št", "Sk"]

        context.update({
            'month_days': month_days,
            'today': today,
            'year': year,
            'month': month,
            'prev_month': prev_month,
            'prev_year': prev_year,
            'next_month': next_month,
            'next_year': next_year,
            'month_name': lt_month_names[month],
            'day_names': lt_day_abbr,
            'week_num': week_num,
            'prev_week': prev_week,
            'next_week': next_week,
            'week_range_str': week_range_str,
        })
        return context




# Registration and Login Views
class ClientRegisterView(View):
    def get(self, request):
        form = ClientRegisterForm()
        return render(request, 'calendar_app/client_register.html', {'form': form})

    def post(self, request):
        form = ClientRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.first_name = user.username
            user.save()
            login(request, user)
            return redirect('calendar')
        return render(request, 'calendar_app/client_register.html', {'form': form})




class ClientLoginView(View):
    def get(self, request):
        form = ClientLoginForm()
        return render(request, 'calendar_app/client_login.html', {'form': form})

    def post(self, request):
        form = ClientLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('calendar')
        return render(request, 'calendar_app/client_login.html', {'form': form})



class CustomLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('calendar')




# Profile and Tag Management
class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        form = ProfileForm(instance=request.user)
        password_form = CustomPasswordChangeForm(request.user, prefix='password')
        tags = EventTag.objects.filter(client=request.user)
        roles = PersonRole.objects.filter(client=request.user)
        add_tag_form = EventTagForm()
        add_role_form = PersonRoleForm()
        return render(request, 'calendar_app/profile.html', {
            'form': form,
            'tags': tags,
            'roles': roles,
            'edit_tag_id': None,
            'edit_tag_form': None,
            'edit_role_id': None,
            'edit_role_form': None,
            'password_form': password_form,
            'add_tag_form': add_tag_form,
            'add_role_form': add_role_form,
        })

    def post(self, request):
        edit_tag_id = None
        edit_tag_form = None
        edit_role_id = None
        edit_role_form = None
        password_form = CustomPasswordChangeForm(request.user, request.POST or None, prefix='password')
        add_tag_form = EventTagForm()
        add_role_form = PersonRoleForm()
        roles = PersonRole.objects.filter(client=request.user)
        tags = EventTag.objects.filter(client=request.user)

        # TAGS
        if 'save_tag' in request.POST and request.POST.get('edit_tag_id'):
            edit_tag_id = int(request.POST.get('edit_tag_id'))
            edit_tag = EventTag.objects.get(id=edit_tag_id, client=request.user)
            edit_tag_form = EventTagForm(request.POST, instance=edit_tag)
            form = ProfileForm(instance=request.user)
            if edit_tag_form.is_valid():
                edit_tag_form.save()
                messages.success(request, "Žyma atnaujinta sėkmingai.")
                return redirect('profile')
        elif 'edit' in request.POST and request.POST.get('edit_tag_id'):
            edit_tag_id = int(request.POST.get('edit_tag_id'))
            edit_tag = EventTag.objects.get(id=edit_tag_id, client=request.user)
            edit_tag_form = EventTagForm(instance=edit_tag)
            form = ProfileForm(instance=request.user)
        elif 'add_tag' in request.POST:
            form = ProfileForm(instance=request.user)
            add_tag_form = EventTagForm(request.POST)
            if add_tag_form.is_valid():
                tag = add_tag_form.save(commit=False)
                tag.client = request.user
                tag.save()
                messages.success(request, "Žyma pridėta sėkmingai.")
                return redirect('profile')

        # ROLES
        elif 'save_role' in request.POST and request.POST.get('edit_role_id'):
            edit_role_id = int(request.POST.get('edit_role_id'))
            edit_role = PersonRole.objects.get(id=edit_role_id, client=request.user)
            edit_role_form = PersonRoleForm(request.POST, instance=edit_role)
            form = ProfileForm(instance=request.user)
            if edit_role_form.is_valid():
                edit_role_form.save()
                messages.success(request, "Rolė atnaujinta sėkmingai.")
                return redirect('profile')
        elif 'edit_role' in request.POST and request.POST.get('edit_role_id'):
            edit_role_id = int(request.POST.get('edit_role_id'))
            edit_role = PersonRole.objects.get(id=edit_role_id, client=request.user)
            edit_role_form = PersonRoleForm(instance=edit_role)
            form = ProfileForm(instance=request.user)
        elif 'add_role' in request.POST:
            form = ProfileForm(instance=request.user)
            add_role_form = PersonRoleForm(request.POST)
            if add_role_form.is_valid():
                role = add_role_form.save(commit=False)
                role.client = request.user
                role.save()
                messages.success(request, "Rolė pridėta sėkmingai.")
                return redirect('profile')
        elif 'delete_role' in request.POST and request.POST.get('delete_role_id'):
            role = PersonRole.objects.get(id=request.POST.get('delete_role_id'), client=request.user)
            role.delete()
            messages.success(request, "Rolė ištrinta sėkmingai.")
            return redirect('profile')

        # PASSWORD
        elif 'change_password' in request.POST:
            form = ProfileForm(instance=request.user)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Slaptažodis pakeistas sėkmingai.")
                return redirect('profile')
        else:
            form = ProfileForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, "Profilis atnaujintas sėkmingai")
                return redirect('profile')

        return render(request, 'calendar_app/profile.html', {
            'form': form,
            'tags': tags,
            'roles': roles,
            'edit_tag_id': edit_tag_id,
            'edit_tag_form': edit_tag_form,
            'edit_role_id': edit_role_id,
            'edit_role_form': edit_role_form,
            'password_form': password_form,
            'add_tag_form': add_tag_form,
            'add_role_form': add_role_form,
        })



class TagDeleteView(LoginRequiredMixin, DeleteView):
    model = EventTag
    template_name = 'calendar_app/tag_confirm_delete.html'
    success_url = reverse_lazy('profile')

    def get_queryset(self):
        return EventTag.objects.filter(client=self.request.user)