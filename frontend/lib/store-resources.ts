import type { Collection, Product, SEOResource, Store, StorePage } from "@/lib/types";

const bodyFromHtml = (value?: string | null) => (value ?? "").replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();

export function storefrontUrl(store: Store | null | undefined, path = "") {
  if (!store?.shop_domain) return path || "";
  const domain = store.shop_domain.replace(/^https?:\/\//, "").replace(/\/$/, "");
  return `https://${domain}${path}`;
}

export function productToResource(store: Store, product: Product): SEOResource {
  return {
    id: product.id,
    resource_type: "product",
    url: storefrontUrl(store, `/products/${product.handle}`),
    title: product.title,
    body: bodyFromHtml(product.description),
    headings: product.title ? [product.title] : [],
    seo_title: product.seo_title,
    meta_description: product.seo_description,
    published: product.status?.toLowerCase() === "active",
    indexable: !product.is_deleted,
    metadata: { vendor: product.vendor, product_type: product.product_type, shopify_id: product.shopify_id },
  };
}

export function collectionToResource(store: Store, collection: Collection): SEOResource {
  return {
    id: collection.id,
    resource_type: "collection",
    url: storefrontUrl(store, `/collections/${collection.handle}`),
    title: collection.title,
    body: bodyFromHtml(collection.description),
    headings: collection.title ? [collection.title] : [],
    seo_title: collection.seo_title,
    meta_description: collection.seo_description,
    metadata: { products_count: collection.products_count, shopify_id: collection.shopify_id },
  };
}

export function pageToResource(store: Store, page: StorePage): SEOResource {
  return {
    id: page.id,
    resource_type: "page",
    url: storefrontUrl(store, `/pages/${page.handle}`),
    title: page.title,
    body: bodyFromHtml(page.body_html),
    headings: page.title ? [page.title] : [],
    seo_title: page.seo_title,
    meta_description: page.seo_description,
    published: page.is_published,
    metadata: { shopify_id: page.shopify_id },
  };
}
