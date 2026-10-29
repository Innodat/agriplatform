/** Exact application-owned routes for disposable local hosts; API owners still authorize. */
export const kdgLocalApiRoutes=Object.freeze([
 '/api/v1/context',
 {path:'/api/v1/provision',maxResponseBytes:1048576},
 {path:'/api/v1/captures',maxResponseBytes:2097152},
 {path:'/api/v1/captures/{uuid}',maxResponseBytes:524288},
 {path:'/api/v1/captures/{uuid}/edit-context',maxResponseBytes:557056},
 {path:'/api/v1/operations/{uuid}',maxResponseBytes:16384},
 {path:'/api/v1/captures',method:'POST',maxRequestBytes:131072,maxResponseBytes:16384},
 {path:'/api/v1/captures/{uuid}',method:'PUT',maxRequestBytes:131072,maxResponseBytes:16384},
 {path:'/api/v1/admin/captures',maxResponseBytes:2097152},
 {path:'/api/v1/admin/captures/{uuid}',maxResponseBytes:524288},
 {path:'/api/v1/admin/captures/{uuid}/audit-details',maxResponseBytes:328704}
].map(route=>typeof route==='string'?route:Object.freeze(route)));
