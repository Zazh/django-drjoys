from modeltranslation.translator import register, TranslationOptions

from .models import Category, Product, Characteristic, UnitOfMeasure, FAQ


@register(Category)
class CategoryTO(TranslationOptions):
    fields = ('name', 'description', 'meta_title', 'meta_description')


@register(Product)
class ProductTO(TranslationOptions):
    fields = ('name', 'tagline', 'description', 'meta_title', 'meta_description')


@register(Characteristic)
class CharacteristicTO(TranslationOptions):
    fields = ('name',)


@register(UnitOfMeasure)
class UnitOfMeasureTO(TranslationOptions):
    fields = ('name',)


@register(FAQ)
class FAQTO(TranslationOptions):
    fields = ('question', 'answer')
