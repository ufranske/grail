import inspect

from nose.tools import assert_not_equal

import grail.settings as settings


class StepResults(object):
    PASSED = 'PASSED'
    FAILED = 'FAILED'
    IGNORED = 'IGNORED'
    PENDING = 'PENDING'
    ERROR = 'ERROR'


def unicode_replace(object_):
    try:
        return unicode(object_)
    except UnicodeDecodeError:
        return unicode(str(object_), errors='replace')


class StepInfo(object):
    description = ''
    pending = False
    step_group = False
    format_description = False
    treat_nested_steps_as_methods = False
    log_input = True
    log_output = True
    function = None
    args = None
    kwargs = None

    def _get_clean_params(self):
        args = self.args
        if args:
            args_def = inspect.getargspec(self.function)[0]
            if args_def and args_def[0] == u'self':
                args = args[1:]
        return args, self.kwargs

    def _get_name_based_description(self):
        return u' '.join(self.function.func_name.split('_'))

    def _get_arguments_string(self):
        args, kwargs = self._get_clean_params()
        if settings.export_mode:
            args = [arg for arg in args if arg]
            kwargs = {k: v for k, v in kwargs.items() if v}
        if len(args) == 0 and len(kwargs) == 0:
            return ''
        args = map(unicode_replace, args)
        kw_arguments = [u'{0}={1}'.format(k, v) for k, v in kwargs.items()]
        return u' (' + u', '.join(args + kw_arguments) + u')'

    def run_function(self):
        return self.function(*self.args, **self.kwargs)

    def get_description(self, output, result, exception_instance):
        message = ''
        if settings.export_mode:
            assert_not_equal(result, StepResults.FAILED, 'Unexpected failure during export')
        else:
            message += result + ' '
        if self.format_description:
            args, kwargs = self._get_clean_params()
            message += self.description.format(*args, **kwargs)
        else:
            message += self.description or self._get_name_based_description()
            if self.log_input:
                message += self._get_arguments_string()
        if self.log_output and output:
            message += u' -> ' + unicode_replace(output)
        if exception_instance:
            message += u': %s' % unicode_replace(exception_instance)
        return message
