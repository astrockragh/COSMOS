# import os


# def _make_psf(self, xlims, ylims, override=False, sextractor_only=False, psfex_only=False):
#     # Set filenames
#     psf_dir = conf.PSF_DIR
#     unclean_cat = os.path.join(conf.PSF_DIR, f'{self.bands}.ldac')
#     psf_cat = os.path.join(conf.PSF_DIR, f'{self.bands}_clean.ldac')
#     path_savexml = conf.PSF_DIR
#     path_savechkimg = ','.join([os.path.join(conf.PSF_DIR, ext)
#                                 for ext in ('chi', 'proto', 'samp', 'resi', 'snap')])
#     path_savechkplt = ','.join([os.path.join(conf.PSF_DIR, ext) for ext in (
#         'fwhm', 'ellipticity', 'counts', 'countfrac', 'chi2', 'resi')])
#     # run SEXTRACTOR in LDAC mode
#     if (not os.path.exists(psf_cat)) | override:

#         if not psfex_only:
#             try:
#                 # -BACK_TYPE MANUAL -BACK_VALUE 0.00001')
#                 os.system(f'sex {self.path_image} -c config/config_psfex.sex -PARAMETERS_NAME config/param_psfex.sex -CATALOG_NAME {unclean_cat} -CATALOG_TYPE FITS_LDAC -MAG_ZEROPOINT {self.mag_zeropoints} ')
#                 self.logger.info('SExtractor succeded!')
#             except:
#                 raise ValueError('SExtractor failed!')
#         self.logger.debug(f'LDAC crop parameters: {xlims}, {ylims}')
#         # open up output SE catalog
#         hdul_ldac = fits.open(
#             unclean_cat, ignore_missing_end=True, mode='update')
#         tab_ldac = hdul_ldac['LDAC_OBJECTS'].data
#         # report to user
#         n_obj = len(tab_ldac)
#         self.logger.debug(f'{n_obj} sources found.')
#         # plot stuff
#         if conf.PLOT > 0:
#             self.logger.debug('Plotting LDAC without pointsource bounding box')
#             plot_ldac(tab_ldac, self.bands, box=False)

#         # Make superselection of safe pointsources within box
#         mask_ldac = (tab_ldac['MAG_AUTO'] > ylims[0]) &\
#             (tab_ldac['MAG_AUTO'] < ylims[1]) &\
#             (tab_ldac['FLUX_RADIUS'] > xlims[0]) &\
#             (tab_ldac['FLUX_RADIUS'] < xlims[1])
#         self.logger.info(
#             f'Found {np.sum(mask_ldac)} objects from box to determine PSF')

#         # X-match to ACS catalog
#         # NOTE: the rightmost vertical strip of COSMOS is not covered by ACS!
#         if conf.USE_STARCATALOG:
#             self.logger.debug(
#                 f'Crossmatching to star catalog {conf.STARCATALOG_FILENAME} with thresh = {conf.STARCATALOG_MATCHRADIUS}')
#             table_star = Table.read(os.path.join(
#                 conf.STARCATALOG_DIR, conf.STARCATALOG_FILENAME))
#             if conf.FLAG_STARCATALOG is not None:
#                 self.logger.debug(
#                     f'Cleaning star catalog {conf.STARCATALOG_FILENAME}')
#                 mask_star = np.ones(len(table_star), dtype=bool)
#                 for selection in conf.FLAG_STARCATALOG:
#                     self.logger.debug(f'   ...where {selection}')
#                     col, val = selection.split('==')
#                     mask_star &= (table_star[col] == int(val))
#                 table_star = table_star[mask_star]
#             ra, dec = table_star[conf.STARCATALOG_COORDCOLS[0]
#                                  ], table_star[conf.STARCATALOG_COORDCOLS[1]]
#             starcoords = SkyCoord(ra=ra * u.deg, dec=dec * u.deg)
#             thresh = conf.STARCATALOG_MATCHRADIUS * u.arcsec
#             head = fits.getheader(self.path_image, 0)
#             w = WCS(head)
#             x, y = tab_ldac['X_IMAGE'], tab_ldac['Y_IMAGE']
#             ral, decl = w.all_pix2world(x, y, 1)
#             candcoords = SkyCoord(ra=ral * u.deg, dec=decl * u.deg)
#             __, d2d, __ = candcoords.match_to_catalog_sky(starcoords)
#             self.logger.info(
#                 f'Found {np.sum(d2d < thresh)} objects from {conf.STARCATALOG_FILENAME} to determine PSF')
#             mask_ldac &= (d2d < thresh)
#         # Check if anything is left. If not, make a scene.
#         n_obj = np.sum(mask_ldac)
#         if n_obj == 0:
#             raise ValueError('No sources selected.')
#         self.logger.info(f'Found {n_obj} objects to determine PSF')
#         # more plotting
#         if conf.PLOT > 0:
#             self.logger.debug('Plotting LDAC with pointsource bounding box')
#             plot_ldac(tab_ldac, self.bands, xlims=xlims,
#                       ylims=ylims, box=True, sel=mask_ldac)
#         # Write out clean catalog with superselection + ACS match
#         hdul_ldac['LDAC_OBJECTS'].data = tab_ldac[mask_ldac]
#         hdul_ldac.writeto(psf_cat, overwrite=override)
#         # RUN PSFEx
#         if not sextractor_only:
#             psfvar_nsnap = 1
#             if self.bands not in conf.CONSTANT_PSF:
#                 psfvar_nsnap = conf.PSFVAR_NSNAP
#                 self.logger.info(
#                     f'Creating spatially-varying PSF with PSFNSNAP = {psfvar_nsnap}')
#             else:
#                 self.logger.info(f'Creating constant PSF')
#             cmd = f'psfex {psf_cat} -c config/config.psfex -BASIS_TYPE PIXEL -PSF_DIR {psf_dir} -PSFVAR_NSNAP {psfvar_nsnap} -WRITE_XML Y -XML_NAME {path_savexml} -CHECKIMAGE_NAME {path_savechkimg} -CHECKPLOT_NAME {path_savechkplt}'
#             self.logger.debug(cmd)
#             os.system(cmd)
#             # Try to move the _clean.psf to .psf
#             try:
#                 oldpath = os.path.join(psf_dir, self.bands+"_clean.psf")
#                 newpath = os.path.join(psf_dir, self.bands+".psf")
#                 self.logger.debug(f'Moving {oldpath} to {newpath}')
#                 os.system(f'mv {oldpath} {newpath}')
#             except:
#                 self.logger.warning(f'Could not move {oldpath} to {newpath} ')
#     else:
#         self.logger.critical(
#             'No PSF attempted. PSF LDAC already exists and override is off')
