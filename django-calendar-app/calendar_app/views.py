import calendar
from django.contrib import messages
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, FormView, TemplateView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Client, Person, Event, EventTag
from .forms import (
    ClientRegisterForm, PersonRegistrationForm, EventForm, ProfileForm, EventTagForm
)
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm


# Person Views
class PersonListView(LoginRequiredMixin, ListView):
    model = Person
    template_name = 'calendar_app/person_list.html'
    context_object_name = 'people'

    def get_queryset(self):
        return Person.objects.filter(client=self.request.user)

class PersonDetailView(LoginRequiredMixin, DetailView):
    model = Person
    template_name = 'calendar_app/person_detail.html'
    context_object_name = 'person'

    def get_queryset(self):
        return Person.objects.filter(client=self.request.user)

class PersonCreateView(LoginRequiredMixin, CreateView):
    model = Person
    form_class = PersonRegistrationForm
    template_name = 'calendar_app/person_registration.html'
    success_url = reverse_lazy('person_list')

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
            form.add_error(None, "Please select a person or enter name and surname manually.")
            return self.form_invalid(form)
        return super().form_valid(form)

class EventDetailView(LoginRequiredMixin, DetailView):
    model = Event
    template_name = 'calendar_app/event_detail.html'
    context_object_name = 'event'

    def get_queryset(self):
        return Event.objects.filter(client=self.request.user)


# Calendar View
class CalendarView(TemplateView):
    template_name = 'calendar_app/calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        year = int(self.request.GET.get('year', today.year))
        month = int(self.request.GET.get('month', today.month))
        week_num = int(self.request.GET.get('week', today.isocalendar()[1]))

        cal = calendar.Calendar(firstweekday=0)
        month_days = []
        week_list = []
        for week in cal.monthdatescalendar(year, month):
            week_days = []
            for day in week:
                events = Event.objects.filter(date=day)
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
        week_range_str = f"{first_day.strftime('%B')} {first_day.day}-{last_day.day}"

        prev_month = month - 1 if month > 1 else 12
        prev_year = year if month > 1 else year - 1
        next_month = month + 1 if month < 12 else 1
        next_year = year if month < 12 else year + 1

        day_names = list(calendar.day_abbr)

        context.update({
            'month_days': month_days,
            'today': today,
            'year': year,
            'month': month,
            'prev_month': prev_month,
            'prev_year': prev_year,
            'next_month': next_month,
            'next_year': next_year,
            'month_name': calendar.month_name[month],
            'day_names': day_names,
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
        form = AuthenticationForm()
        return render(request, 'calendar_app/client_login.html', {'form': form})

    def post(self, request):
        form = AuthenticationForm(request, data=request.POST)
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
        password_form = PasswordChangeForm(request.user, prefix='password')
        tags = EventTag.objects.filter(client=request.user)
        return render(request, 'calendar_app/profile.html', {
            'form': form,
            'tags': tags,
            'edit_tag_id': None,
            'edit_tag_form': None,
            'password_form': password_form,
        })

    def post(self, request):
        edit_tag_id = None
        edit_tag_form = None
        password_form = PasswordChangeForm(request.user, request.POST or None, prefix='password')
        if 'save_tag' in request.POST and request.POST.get('edit_tag_id'):
            edit_tag_id = int(request.POST.get('edit_tag_id'))
            edit_tag = EventTag.objects.get(id=edit_tag_id, client=request.user)
            edit_tag_form = EventTagForm(request.POST, instance=edit_tag)
            form = ProfileForm(instance=request.user)
            if edit_tag_form.is_valid():
                edit_tag_form.save()
                messages.success(request, "Tag updated successfully.")
                return redirect('profile')
        elif 'edit' in request.POST and request.POST.get('edit_tag_id'):
            edit_tag_id = int(request.POST.get('edit_tag_id'))
            edit_tag = EventTag.objects.get(id=edit_tag_id, client=request.user)
            edit_tag_form = EventTagForm(instance=edit_tag)
            form = ProfileForm(instance=request.user)
        elif 'change_password' in request.POST:
            form = ProfileForm(instance=request.user)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Password changed successfully.")
                return redirect('profile')
        else:
            form = ProfileForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, "Profile updated successfully.")
                return redirect('profile')
        tags = EventTag.objects.filter(client=request.user)
        return render(request, 'calendar_app/profile.html', {
            'form': form,
            'tags': tags,
            'edit_tag_id': edit_tag_id,
            'edit_tag_form': edit_tag_form,
            'password_form': password_form,
        })

class TagListView(LoginRequiredMixin, ListView):
    model = EventTag
    template_name = 'calendar_app/tag_list.html'
    context_object_name = 'tags'

    def get_queryset(self):
        return EventTag.objects.filter(client=self.request.user)

class TagCreateView(LoginRequiredMixin, CreateView):
    model = EventTag
    form_class = EventTagForm
    template_name = 'calendar_app/tag_form.html'
    success_url = reverse_lazy('tag_list')

    def form_valid(self, form):
        form.instance.client = self.request.user
        return super().form_valid(form)

class TagEditView(LoginRequiredMixin, UpdateView):
    model = EventTag
    form_class = EventTagForm
    template_name = 'calendar_app/tag_form.html'
    success_url = reverse_lazy('tag_list')

    def get_queryset(self):
        return EventTag.objects.filter(client=self.request.user)

class TagDeleteView(LoginRequiredMixin, DeleteView):
    model = EventTag
    template_name = 'calendar_app/tag_confirm_delete.html'
    success_url = reverse_lazy('tag_list')

    def get_queryset(self):
        return EventTag.objects.filter(client=self.request.user)