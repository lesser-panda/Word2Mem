from django.shortcuts import redirect, render


class ObjectCreateMixin:
    form_class = None
    template_name = ''

    def get(self, request):
        return render(
            request,
            self.template_name,
            {'form': self.form_class}
        )

    def post(self, request):
        bound_form = self.form_class(request.POST)
        if bound_form.is_valid():
            new_object = bound_form.save()
            if self.template_name == "wordbook/word_collection_create.html":
                request.user.vc_list.add(new_object)
            return redirect(new_object)
        else:
            return render(
                request,
                self.template_name,
                {'form': bound_form}
            )
