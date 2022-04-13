export const getResourceVersions = (resource: any) => {
    return resource.data?.items?.map((item: any) => item.metadata.resourceVersion)
}