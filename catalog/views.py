from django.shortcuts import render
from .models import Book, Author, BookInstance, Genre
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime
from .forms import RenewBookForm
from django.contrib.auth.decorators import permission_required
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Author


# Create your views here.


def index(request):
    """
    Función vista para la página de inicio del sitio
    
    """
    #Genera contadores de algunos de los objetos principales

    num_books= Book.objects.all().count()
    num_instances= BookInstance.objects.all().count()

    #libros disponibles (status = 'a')

    num_instances_available = BookInstance.objects.filter(status__exact = 'a').count()
    num_authors = Author.objects.count() # El 'all()' está implícito por defecto.

    # Numero de Visitas a esta view, como esta contado en la variable de sesión

    num_visits = request.session.get('num_visits', 0)
    num_visits += 1
    request.session['num_visits']= num_visits
    
    #tarea a la que te reta mozilla

    num_genre = Genre.objects.all().count()
    num_filter_cap = Book.objects.filter(title__icontains = 'a').count()

    #Renderiza la plantilla HTML index.html con los datos en la variable contexto

    return render(
        request,
        'index.html',
        context=
            {'num_books': num_books, 'num_instances': num_instances, 
            'num_instances_available': num_instances_available, 'num_authors': num_authors,
            'num_genre': num_genre, 'num_filter_cap': num_filter_cap, 'num_visits':num_visits, }
    )

class BookListView(generic.ListView):
    model = Book
    context_object_name = 'book_list' #su propio nombre para la lista como variable de plantilla
    
class BookDetailView(generic.DetailView):
    model = Book
    paginate_by = 10

class AuthorListView(generic.ListView):
    model = Author
    context_object_name = 'authors_list'

class AuthorDetailView(generic.DetailView):
    model = Author
    paginate_by = 10

class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """
    Vista genérica basada en clases que enumera los libros prestados al usuario actual.
    """
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

class AllLoanedBooksListView(PermissionRequiredMixin,generic.ListView):
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/bookinstance_list_borrowed_all.html'
    paginate_by = 10

    def get_queryset(self):
        #Filtramos por estado 'o' (on Loan / en préstamo) y ordenamos por fecha
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')


@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    """
    View function for renewing a specific BookInstance by librarian
    """
    book_inst=get_object_or_404(BookInstance, pk = pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed') )

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date,})

    return render(request, 'catalog/book_renew_librarian.html', {'form': form, 'bookinst':book_inst})

class AuthorCreate(CreateView):
    model = Author
    fields = '__all__'
    initial={'date_of_death':'05/01/2018',}

class AuthorUpdate(UpdateView):
    model = Author
    fields = ['first_name','last_name','date_of_birth','date_of_death']

class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')